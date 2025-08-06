# MCQ Generator

An intelligent Multiple Choice Question generator for engineering lectures using Google AI Studio (Gemini API) and Streamlit.

## Features

- 🤖 AI-powered MCQ generation from lecture topics
- 📝 Interactive quiz interface with immediate feedback
- 📊 Detailed results and explanations
- 🔄 Progress tracking
- 🔄 Easy regeneration of new quizzes

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Google AI Studio API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the API key

3. **Configure Environment**
   - Rename `.env.example` to `.env`
   - Add your API key: `GOOGLE_API_KEY=your_api_key_here`

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Enter Lecture Topics**: Provide a comprehensive summary of your lecture topics
2. **Add AI Instructions** (Optional): Give specific guidance for question generation
3. **Generate MCQs**: Click to create 3 AI-generated questions
4. **Take the Quiz**: Answer questions one by one with immediate feedback
5. **Review Results**: See your score and detailed explanations

## System Requirements

- Python 3.8+
- Internet connection for API calls
- Google AI Studio API key

## Troubleshooting

- **API Key Issues**: Ensure your Google AI Studio API key is valid and has sufficient quota
- **JSON Parsing Errors**: The AI might occasionally return malformed JSON. Try regenerating the quiz
- **Network Issues**: Check your internet connection for API calls

## License

MIT License 