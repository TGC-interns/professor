import streamlit as st
from firebase_helper import init_firestore
import google.generativeai as genai
import json
import os
import random
import time

st.set_page_config(page_title="Exit Ticket Generator - Teacher Portal", layout="wide")

from config import DEFAULT_QUESTIONS_COUNT
from ui import app_ui

db = init_firestore()

# Subject list for dropdown
subjects = ["Cloud Computing", "Machine Learning", "Cybersecurity", "Data Structures", "Networking"]

GOOGLE_API_KEY = st.secrets["api_keys"]["google_api_key"]

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Enhanced system prompt for better API integration
SYSTEM_PROMPT = """You are a highly qualified MCQ generator for an engineering college lecture. Your task is to create exactly {num_questions} multiple-choice questions (MCQs) based strictly on the list of topics provided from a lecture. These MCQs serve as exit ticket questions to assess students' understanding of core concepts.

Instructions:
- Only use concepts that were explicitly covered in the given topic list
- Do not include or infer content beyond the provided topics
- Focus on the most essential technical points, definitions, principles, or equations
- Each question must have one correct answer and three plausible distractors
- Generate exactly 4 options, no more and no less
- Ensure that not more than 2 consecutive correct answers use the same option identifier (A, B, C, or D) to maintain balance across all choices
- Options are identified by bullet points
- The correct answer must be factually accurate
- Write short, clear, and professional questions and answer choices
- Use standard engineering terminology and units
- Keep all technical details precise and concise

Output Format (JSON):
{
  "questions": [
    {
      "question": "Question text here?",
      "options": {
        "A": "Option A text",
        "B": "Option B text", 
        "C": "Option C text",
        "D": "Option D text"
      },
      "correct_answer": "A",
      "explanation": "Brief explanation of why this answer is correct",
      "topic": "Main topic of the question",
      "subtopic": "Subtopic or Specific concept of focus area"
    }
  ]
}

Requirements:
- Return ONLY valid JSON format
- Ensure all questions are relevant to the provided topics and the subject
- Do not deviate and hallucinate from the subject
- Make explanations educational and clear
- Each question MUST include both a "topic" and "subtopic" field. These are mandatory.
- Use engineering-appropriate language and precision"""

def generate_mcqs(lecture_topics, ai_instructions, num_questions, subject):
    """Generate MCQs using Google AI Studio"""
    try:
        if not GOOGLE_API_KEY:
            st.error("Google API key not found. Please set GOOGLE_API_KEY in your environment variables.")
            return None
        
        # Create the prompt with system prompt
        prompt = f"""{SYSTEM_PROMPT}

Subject:
{subject}

Lecture Topics:
{lecture_topics}

Additional Instructions:
{ai_instructions if ai_instructions.strip() else "No additional instructions provided."}

Please generate exactly {num_questions} MCQs based on the above topics and instructions. Do not generate fewer or more.

Return ONLY the JSON format as specified above."""

        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response
            response_text = response.text
            # Find JSON content (handle cases where response might have extra text)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            mcqs = json.loads(json_str)
            
            from firebase_helper import save_question
            for q in mcqs.get("questions", []):
                q["subject"] = subject
                save_question(db, q, source="ai")
            
            return mcqs
            
        except json.JSONDecodeError as e:
            st.error(f"Error parsing AI response: {e}")
            st.text("Raw response:")
            st.text(response.text)
            return None
            
    except Exception as e:
        st.error(f"Error generating MCQs: {e}")
        return None

def regenerate_teacher_question(question_index, subject, topics, instructions):
    """Regenerate a single question for teachers"""
    with st.spinner("🔄 Regenerating question..."):
        # Generate a single question
        mcqs = generate_mcqs(topics, instructions, 1, subject)
        
        if mcqs and 'questions' in mcqs and len(mcqs['questions']) > 0:
            # Replace the question at the given index
            st.session_state.teacher_all_mcqs[question_index] = mcqs['questions'][0]
            st.success("✅ Question regenerated successfully!")
            st.rerun()
        else:
            st.error("Failed to regenerate question. Please try again.")

def main():    
    st.markdown(
        app_ui,
        unsafe_allow_html=True
    )
    
    # Single teacher access - no login required
    st.sidebar.success("🎓 Teacher Portal")
    
    # Direct to teacher dashboard
    teacher_dashboard()

def teacher_dashboard():
    st.sidebar.title("👩‍🏫 Teacher Dashboard")
    page = st.sidebar.radio("Navigate", ["📘 Create Exit Ticket", "🎫 My Published Tickets"])
    
    if page == "📘 Create Exit Ticket":
        st.title("🎓 Create Exit Ticket")
        st.markdown("""
        Exit tickets are quick assessments at the end of a lesson to check students' understanding.
        Teachers can use AI to generate MCQs based on the lecture content to include in exit tickets.
        """)
        
        # Initialize teacher-specific session state
        for key, default in {
            "teacher_mcqs": None,
            "teacher_all_mcqs": None,
            "teacher_ready_for_review": False
        }.items():
            if key not in st.session_state:
                st.session_state[key] = default
        
        # Flow control for teachers
        if st.session_state.teacher_mcqs is None:
            show_teacher_input_page()
        elif not st.session_state.teacher_ready_for_review:
            show_teacher_questions_page()
        else:
            show_teacher_input_page()  # Reset to input page after review
    
    elif page == "🎫 My Published Tickets":
        view_published_tickets_page()

def show_teacher_input_page():
    """Input page specifically for teachers"""
    
    st.markdown(
        app_ui,
        unsafe_allow_html=True
    )
    
    st.markdown("Enter all details marked with `*` to generate MCQs")
    st.header("📝 Enter Lecture Information")
    
    with st.form("teacher_mcq_form"):
        st.markdown("### 📚 Lecture Subject *")
        subject = st.text_area(
            "Enter the subject of your lecture",
            placeholder="e.g., Cloud Computing, Machine Learning, etc.",
            help="Specify the subject for which you want to generate MCQs",
            height=69)
        
        st.markdown("---")
        
        st.markdown("### 📖 Lecture Topics & Summary *")
        lecture_topics = st.text_area(
            "Add a detailed summary of the lecture topics",
            placeholder="Enter the main topics, concepts, and key points covered in your lecture...",
            height=100,
            help="Include all important topics, definitions, formulas, and concepts that were covered"
        )
        
        ai_instruction_options = {
            "None": "",
            "🧠 Focus on conceptual clarity": "Emphasize conceptual understanding of the topics.",
            "🧪 Include numerical or formula-based questions": "Include numerical problems or questions requiring application of formulas.",
            "🛠️ Emphasize real-world applications": "Generate questions that relate the concepts to real-world engineering applications.",
            "🔍 Include commonly misunderstood concepts": "Focus on common misconceptions or tricky areas in the lecture topics.",
            "🎯 Prioritize definition-based questions": "Ask for precise definitions and terminology-based MCQs.",
            "🔄 Convert Above Text Questions into MCQs": "Take the provided descriptive or paragraph-style questions and convert them into multiple-choice format."
        }
        
        st.markdown("---")
        st.subheader("🤖 AI Instructions (Optional)")
        selected_instruction_key = st.selectbox(
            "Additional instructions for AI",
            options=list(ai_instruction_options.keys()),
            help="Choose how the AI should generate your questions"
        )
        ai_instructions = ai_instruction_options[selected_instruction_key]
        
        st.markdown("---")
        st.subheader("🧮 Number of Questions to Generate")
        num_questions = st.slider(
            "Number of questions",
            min_value=3,
            max_value=10,
            value=5,
            help="Generate questions for your exit ticket"
        )
        
        submitted = st.form_submit_button("🚀 Generate MCQs", type="primary")
        
        if submitted:
            if not lecture_topics.strip():
                st.error("Please enter lecture topics to generate MCQs.")
                return
            
            with st.spinner("🤖 Generating MCQs with AI..."):
                mcqs = generate_mcqs(lecture_topics, ai_instructions, num_questions, subject)
                
                if mcqs and 'questions' in mcqs:
                    if len(mcqs['questions']) < num_questions:
                        st.error(f"Only {len(mcqs['questions'])} questions were generated. Please try again or reduce the count.")
                        return
                    
                    # Store in teacher-specific session state
                    st.session_state.teacher_subject = subject
                    st.session_state.teacher_lecture_topics = lecture_topics
                    st.session_state.teacher_ai_instructions = ai_instructions
                    st.session_state.teacher_all_mcqs = mcqs['questions']
                    st.session_state.teacher_mcqs = mcqs['questions']
                    st.session_state.teacher_ready_for_review = False
                    
                    st.rerun()
                else:
                    st.error("Failed to generate MCQs. Please try again.")

def show_teacher_questions_page():
    """Display all generated questions for teachers to review and edit"""
    st.header("📚 Generated Questions - Review & Edit")
    
    if 'teacher_all_mcqs' not in st.session_state or not st.session_state.teacher_all_mcqs:
        st.warning("⚠️ No questions found. Please generate questions first.")
        return

    all_mcqs = st.session_state.teacher_all_mcqs
    subject = st.session_state.get("teacher_subject", "")
    topics = st.session_state.get("teacher_lecture_topics", "")
    instructions = st.session_state.get("teacher_ai_instructions", "")

    st.markdown(f"**Subject:** {subject}")
    st.markdown(f"**Total Questions Generated:** {len(all_mcqs)}")
    st.markdown("---")

    for i, question_data in enumerate(all_mcqs):
        edit_key = f"teacher_edit_mode_{i}"
        if edit_key not in st.session_state:
            st.session_state[edit_key] = False

        with st.expander(f"Question {i + 1}: {question_data['question'][:50]}..."):
            if not st.session_state[edit_key]:
                st.markdown(f"**Question:** {question_data['question']}")

                for option, text in question_data['options'].items():
                    if option == question_data['correct_answer']:
                        st.markdown(f"✅ **{option}) {text}** (Correct Answer)")
                    else:
                        st.markdown(f"{option}) {text}")

                st.markdown(f"**Explanation:** {question_data.get('explanation', 'No explanation provided.')}")
                st.markdown(f"**Topic:** {question_data.get('topic', 'Unknown')}")
                st.markdown(f"**Subtopic:** {question_data.get('subtopic', 'Unknown')}")

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("✏️ Edit", key=f"teacher_edit_btn_{i}"):
                        st.session_state[edit_key] = True
                with col2:
                    if st.button("🔁 Regenerate", key=f"teacher_regen_{i}"):
                        regenerate_teacher_question(i, subject, topics, instructions)

            else:
                # EDIT MODE
                st.markdown("### ✏️ Editing Mode")
                edited_question = st.text_area("Edit Question", question_data['question'], key=f"teacher_q_text_{i}")

                edited_options = {}
                correct_option = st.selectbox(
                    "Correct Answer",
                    list(question_data['options'].keys()),
                    index=list(question_data['options'].keys()).index(question_data['correct_answer']),
                    key=f"teacher_correct_{i}"
                )

                for option in sorted(question_data['options'].keys()):
                    edited_options[option] = st.text_input(
                        f"Option {option}",
                        value=question_data['options'][option],
                        key=f"teacher_opt_{i}_{option}"
                    )

                edited_explanation = st.text_area("Explanation", question_data.get('explanation', ''), key=f"teacher_exp_{i}")
                edited_topic = st.text_input("Topic", question_data.get('topic', ''), key=f"teacher_topic_{i}")
                edited_subtopic = st.text_input("Subtopic", question_data.get('subtopic', ''), key=f"teacher_subtopic_{i}")

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("💾 Save", key=f"teacher_save_{i}"):
                        st.session_state.teacher_all_mcqs[i] = {
                            "question": edited_question,
                            "options": edited_options,
                            "correct_answer": correct_option,
                            "explanation": edited_explanation,
                            "topic": edited_topic,
                            "subtopic": edited_subtopic,
                        }
                        st.session_state[edit_key] = False
                        st.success("✅ Question updated.")
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", key=f"teacher_cancel_{i}"):
                        st.session_state[edit_key] = False
                        st.rerun()

    st.markdown("---")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 Generate New Set", key="teacher_generate_new_btn"):
            subject = st.session_state.get("teacher_subject", "")
            topics = st.session_state.get("teacher_lecture_topics", "")
            instructions = st.session_state.get("teacher_ai_instructions", "")
            num_questions = st.session_state.get("teacher_num_questions", 5)  # fallback to 5 if missing

            new_mcqs = generate_mcqs(topics, instructions, num_questions, subject)
            if new_mcqs and 'questions' in new_mcqs:
                st.session_state.teacher_mcqs = new_mcqs['questions']
                st.session_state.teacher_all_mcqs = new_mcqs['questions']
                st.session_state.teacher_ready_for_review = True
                st.success("✅ New questions generated.")
            else:
                st.error("❌ Failed to generate a new set. Please try again.")

    with col2:
        if st.button("📤 PUBLISH Exit Ticket", key="teacher_publish_btn"):
            publish_exit_ticket()

def publish_exit_ticket():
    """Publish the current questions as an exit ticket"""
    try:
        if 'teacher_all_mcqs' not in st.session_state or not st.session_state.teacher_all_mcqs:
            st.error("No questions to publish!")
            return
    
        # Use a default teacher name since there's only one teacher
        teacher_name = "Professor"  # Single teacher system
        subject = st.session_state.get('teacher_subject', 'Unknown Subject')
        lecture_topics = st.session_state.get('teacher_lecture_topics', 'No topics specified')
        questions = st.session_state.teacher_all_mcqs
        
        # Create exit ticket
        from firebase_helper import create_exit_ticket
        ticket = create_exit_ticket(db, questions, teacher_name, subject, lecture_topics)
        
        if ticket:
            st.success(f"🎉 Exit Ticket Published Successfully!")
            st.info(f"**Ticket Code: {ticket['ticket_id']}**")
            st.markdown(f"**Title:** {ticket['title']}")
            st.markdown(f"**Subject:** {ticket['subject']}")
            st.markdown(f"**Total Questions:** {ticket['total_questions']}")
            st.markdown("---")
            st.markdown("📋 **Share this Ticket Code with your students:**")
            st.code(ticket['ticket_id'], language=None)
            st.markdown("Students can use this code to access and answer the exit ticket.")
            
            # Store published ticket info in session state
            st.session_state.published_ticket = ticket
            
            # Reset teacher session state for new generation
            st.session_state.teacher_mcqs = None
            st.session_state.teacher_all_mcqs = None
            st.session_state.teacher_ready_for_review = False
            
        else:
            st.error("Failed to publish exit ticket. Please try again.")
            
    except Exception as e:
        st.error(f"Error publishing exit ticket: {e}")

def view_published_tickets_page():
    """Display all tickets published by the teacher"""
    st.header("🎫 My Published Exit Tickets")
    st.markdown(app_ui, unsafe_allow_html=True)
    
    # Single teacher system - use "Professor" as the teacher name
    teacher_name = "Professor"
    
    from firebase_helper import get_all_tickets_by_teacher
    tickets = get_all_tickets_by_teacher(db, teacher_name)
    
    if not tickets:
        st.info("📭 No exit tickets published yet.")
        st.markdown("Create your first exit ticket using the '📘 Create Exit Ticket' tab!")
        return
    
    st.markdown(f"**Total Published Tickets:** {len(tickets)}")
    st.markdown("---")
    
    # Check if we should show analytics for a specific ticket
    if 'show_analytics_for' in st.session_state:
        view_ticket_analytics(st.session_state.show_analytics_for)
        if st.button("🔙 Back to All Tickets"):
            del st.session_state.show_analytics_for
            st.rerun()
        return
    
    for idx, ticket in enumerate(tickets):
        with st.expander(f"🎫 {ticket.get('title', 'Untitled')} - Code: {ticket['ticket_id']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Ticket Code:** `{ticket['ticket_id']}`")
                st.markdown(f"**Subject:** {ticket.get('subject', 'N/A')}")
                st.markdown(f"**Total Questions:** {ticket.get('total_questions', 0)}")
                st.markdown(f"**Status:** {ticket.get('status', 'unknown').title()}")
                
                # Fixed timestamp handling
                created_at = ticket.get('created_at', 'Unknown')
                try:
                    if hasattr(created_at, 'strftime'):
                        formatted_date = created_at.strftime('%Y-%m-%d %H:%M')
                    elif hasattr(created_at, 'to_pydatetime'):
                        formatted_date = created_at.to_pydatetime().strftime('%Y-%m-%d %H:%M')
                    else:
                        formatted_date = str(created_at)
                except:
                    formatted_date = "Unknown"
                
                st.markdown(f"**Created:** {formatted_date}")
                
                # Show lecture topics
                topics = ticket.get('lecture_topics', '')
                if topics:
                    st.markdown(f"**Topics:** {topics}")
                
                # Show response count
                from firebase_helper import get_ticket_analytics
                analytics = get_ticket_analytics(db, ticket['ticket_id'])
                st.markdown(f"**📊 Responses:** {analytics['total_responses']} | **📈 Avg Score:** {analytics['average_score']}%")
            
            with col2:
                # Action buttons
                if st.button("📋 Copy Code", key=f"copy_id_{idx}"):
                    st.code(ticket['ticket_id'], language=None)
                    st.success("Code ready to copy!")
                
                # View Analytics button
                if st.button("📊 View Analytics", key=f"analytics_{idx}"):
                    st.session_state.show_analytics_for = ticket['ticket_id']
                    st.rerun()
                
                if ticket.get('status') == 'active':
                    if st.button("🔒 Deactivate", key=f"deactivate_{idx}"):
                        from firebase_helper import update_ticket_status
                        if update_ticket_status(db, ticket['ticket_id'], 'inactive'):
                            st.success("Ticket deactivated!")
                            st.rerun()
                        else:
                            st.error("Failed to deactivate ticket.")
                else:
                    if st.button("✅ Activate", key=f"activate_{idx}"):
                        from firebase_helper import update_ticket_status
                        if update_ticket_status(db, ticket['ticket_id'], 'active'):
                            st.success("Ticket activated!")
                            st.rerun()
                        else:
                            st.error("Failed to activate ticket.")
            
            # Questions preview
            questions = ticket.get('questions', [])
            if questions:
                st.markdown("**Questions Preview:**")
                for i, q in enumerate(questions[:2]):
                    question_text = q.get('question', 'No question text')
                    if len(question_text) > 60:
                        question_text = question_text[:60] + "..."
                    st.markdown(f"{i+1}. {question_text}")
                if len(questions) > 2:
                    st.markdown(f"... and {len(questions) - 2} more questions")

def view_ticket_analytics(ticket_id):
    """
    Display analytics and student responses for a specific ticket with flag information
    """
    st.header(f"📊 Analytics for Ticket: {ticket_id}")
    
    from firebase_helper import get_ticket_analytics, get_exit_ticket
    
    # Get ticket info
    ticket_data = get_exit_ticket(db, ticket_id)
    if not ticket_data:
        st.error("Ticket not found!")
        return
    
    # Get analytics
    analytics = get_ticket_analytics(db, ticket_id)
    
    # Display ticket info
    st.markdown(f"**Title:** {ticket_data.get('title', 'N/A')}")
    st.markdown(f"**Subject:** {ticket_data.get('subject', 'N/A')}")
    st.markdown(f"**Total Questions:** {ticket_data.get('total_questions', 0)}")
    st.markdown("---")
    
    # Display analytics metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📝 Total Responses", analytics['total_responses'])
    
    with col2:
        st.metric("👥 Unique Students", analytics.get('unique_students', 0))
    
    with col3:
        st.metric("📊 Average Score", f"{analytics['average_score']}%")
    
    # Calculate and display flag statistics
    if analytics['total_responses'] > 0:
        flag_stats = calculate_flag_statistics(analytics.get('responses', []), ticket_data.get('questions', []))
        
        if flag_stats['total_flags'] > 0:
            st.markdown("---")
            st.subheader("🚩 Question Flag Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🚩 Total Flags", flag_stats['total_flags'])
            with col2:
                st.metric("🏳️ Questions Flagged", f"{flag_stats['flagged_questions']}/{len(ticket_data.get('questions', []))}")
            
            # Show flag details per question
            st.markdown("### 📋 Flags per Question")
            for q_idx, question_flags in flag_stats['question_flag_details'].items():
                if question_flags['flag_count'] > 0:
                    with st.expander(f"🚩 Question {q_idx + 1}: {question_flags['flag_count']} flag(s)"):
                        question_text = question_flags['question_text']
                        st.markdown(f"**Question:** {question_text}")
                        st.error(f"**🚩 Flagged by {question_flags['flag_count']} student(s)**")
                        
                        st.markdown("**Students who flagged this question:**")
                        for student in question_flags['flagged_by']:
                            st.markdown(f"- {student}")
                        
                        st.markdown("**Possible reasons for flagging:**")
                        st.markdown("- Question unclear or confusing")
                        st.markdown("- Content not covered in class") 
                        st.markdown("- Question might be out of syllabus")
                        st.markdown("- Possible error in question or options")
    
    st.markdown("---")
    
    # Display individual responses
    if analytics['total_responses'] > 0:
        st.subheader("📋 Student Responses")
        
        responses = analytics.get('responses', [])
        for i, response in enumerate(responses):
            # Count flags for this student
            student_flags = response.get('flags', {})
            flag_count = len([f for f in student_flags.values() if f])
            flag_indicator = f" 🚩({flag_count})" if flag_count > 0 else ""
            
            with st.expander(f"👤 {response.get('student_name', 'Unknown')} - {response.get('score', {}).get('percentage', 0):.1f}%{flag_indicator}"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"**Score:** {response.get('score', {}).get('correct_count', 0)}/{response.get('score', {}).get('total_questions', 0)}")
                    st.markdown(f"**Percentage:** {response.get('score', {}).get('percentage', 0):.1f}%")
                    if flag_count > 0:
                        st.markdown(f"**🚩 Questions Flagged:** {flag_count}")
                
                with col2:
                    completed_at = response.get('completed_at', 'Unknown')
                    try:
                        if hasattr(completed_at, 'strftime'):
                            formatted_time = completed_at.strftime('%Y-%m-%d %H:%M')
                        elif hasattr(completed_at, 'to_pydatetime'):
                            formatted_time = completed_at.to_pydatetime().strftime('%Y-%m-%d %H:%M')
                        else:
                            formatted_time = str(completed_at)
                    except:
                        formatted_time = "Unknown"
                    
                    st.markdown(f"**Completed:** {formatted_time}")
                
                # Show detailed responses
                st.markdown("**Answers:**")
                responses_dict = response.get('responses', {})
                questions = ticket_data.get('questions', [])
                
                for q_idx_str, student_answer in responses_dict.items():
                    q_idx = int(q_idx_str)  # Convert string back to int for indexing
                    if q_idx < len(questions):
                        question = questions[q_idx]
                        correct_answer = question['correct_answer']
                        
                        # Check if this question was flagged
                        is_flagged = student_flags.get(str(q_idx), False)
                        flag_symbol = " 🚩" if is_flagged else ""
                        
                        # Compare student_answer with correct_answer properly
                        is_correct = student_answer == correct_answer
                        
                        # Show correct status symbol
                        status = "✅" if is_correct else "❌"
                        
                        # Get the text for the student's answer
                        answer_text = question['options'].get(student_answer, 'N/A')
                        
                        st.markdown(f"{status} Q{q_idx+1}: {student_answer}) {answer_text}{flag_symbol}")
                        
                        # Show what the correct answer was if student was wrong
                        if not is_correct:
                            correct_text = question['options'].get(correct_answer, 'N/A')
                            st.markdown(f"    🎯 Correct: {correct_answer}) {correct_text}")
                            
                        # Show flag reason if flagged
                        if is_flagged:
                            st.warning(f"    🚩 Student flagged this question as unclear/out of syllabus")
    else:
        st.info("No student responses yet.")

def calculate_flag_statistics(responses, questions):
    """Calculate flag statistics from student responses"""
    flag_stats = {
        'total_flags': 0,
        'flagged_questions': 0,
        'question_flag_details': {}
    }
    
    # Initialize question details
    for i, question in enumerate(questions):
        flag_stats['question_flag_details'][i] = {
            'question_text': question.get('question', 'Unknown'),
            'flag_count': 0,
            'flagged_by': []
        }
    
    # Count flags from all responses
    for response in responses:
        student_name = response.get('student_name', 'Unknown')
        flags = response.get('flags', {})
        
        for q_idx_str, is_flagged in flags.items():
            if is_flagged:
                q_idx = int(q_idx_str)
                if q_idx in flag_stats['question_flag_details']:
                    flag_stats['question_flag_details'][q_idx]['flag_count'] += 1
                    flag_stats['question_flag_details'][q_idx]['flagged_by'].append(student_name)
                    flag_stats['total_flags'] += 1
    
    # Count how many questions were flagged
    flag_stats['flagged_questions'] = len([
        q for q in flag_stats['question_flag_details'].values() 
        if q['flag_count'] > 0
    ])
    
    return flag_stats

if __name__ == "__main__":
    main()