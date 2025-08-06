app_ui = """
<style>
/* Aggressive light theme override for all buttons and inputs */
body, .stApp, .main .block-container {
    background-color: #F7FAFC !important;
}
/* Card/form backgrounds */
.stForm, .stExpander, .stMetric {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    border: 1px solid #E2E8F0 !important;
}
/* Text colors */
.stMarkdown, .stText, p, div, span, label, .stCaption, .stMetricLabel {
    color: #22223B !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #22223B !important;
    font-weight: 600;
}
/* All buttons: primary, secondary, etc. */
.stButton > button, .stForm button, button, input[type="button"], input[type="submit"] {
    background-color: #43A363 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.2s cubic-bezier(.4,0,.2,1) !important;
    box-shadow: 0 2px 8px rgba(67, 163, 99, 0.10) !important;
    outline: none !important;
}
.stButton > button:hover, .stForm button:hover, button:hover, input[type="button"]:hover, input[type="submit"]:hover {
    background-color: #388752 !important;
}
.stButton > button:active, .stForm button:active, button:active, input[type="button"]:active, input[type="submit"]:active {
    background-color: #2E6B4B !important;
}
/* Backward/secondary buttons (by key) - visually distinct */
button#back_btn {
    background-color: #FFFFFF !important;
    color: #43A363 !important;
    border: 2px solid #43A363 !important;
    box-shadow: 0 2px 8px rgba(67, 163, 99, 0.05) !important;
}
button#back_btn:hover, button#back_btn:focus {
    background-color: #E9F7F0 !important;
    color: #388752 !important;
    border-color: #388752 !important;
}
/* Text inputs and textareas */
.stTextInput input, .stTextArea textarea, input[type="text"], textarea {
    background-color: #FFFFFF !important;
    color: #22223B !important;
    border: 2px solid #E2E8F0 !important;
    border-radius: 8px !important;
    padding: 0.75rem !important;
    caret-color: #22223B !important;
}
.stTextInput input:focus, .stTextArea textarea:focus, input[type="text"]:focus, textarea:focus {
    border-color: #43A363 !important;
    box-shadow: 0 0 0 3px rgba(67, 163, 99, 0.10) !important;
}
/* Radio/toggle buttons - green accent and background */
.stRadio > div {
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
    padding: 1.25rem 2.5rem 1.25rem 1.5rem !important;
    border: 1.5px solid #E2E8F0 !important;
    margin-bottom: 1.1rem !important;
    min-width: 520px !important;
    max-width: 900px !important;
    width: 100% !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    display: flex !important;
    flex-direction: column !important;
}
.stRadio label {
    color: #22223B !important;
    font-weight: 500 !important;
    font-size: 1.08rem !important;
    width: 100%;
}
.stRadio input[type="radio"] {
    accent-color: #B8EFC6 !important; /* light green */
    background-color: #E9F7F0 !important; /* very light green */
}
.stRadio input[type="radio"]:checked {
    accent-color: #43A363 !important; /* green when checked */
    background-color: #DFF3E8 !important;
}
/* Progress bar */
.stProgress > div > div {
    background-color: #43A363 !important;
}
/* Success/Error/Info messages */
.stSuccess {
    background-color: #DCFCE7 !important;
    color: #166534 !important;
    border-left: 4px solid #43A363 !important;
    padding: 1rem !important;
    border-radius: 8px !important;
}
.stError {
    background-color: #FEE2E2 !important;
    color: #B91C1C !important;
    border-left: 4px solid #EF4444 !important;
    padding: 1rem !important;
    border-radius: 8px !important;
}
.stInfo {
    background-color: #DBEAFE !important;
    color: #1E40AF !important;
    border-left: 4px solid #2563EB !important;
    padding: 1rem !important;
    border-radius: 8px !important;
}
/* Expander header */
.stExpanderHeader {
    color: #22223B !important;
    background-color: #F1F5F9 !important;
    border-radius: 8px 8px 0 0 !important;
}
/* Links */
a {
    color: #43A363 !important;
    text-decoration: underline !important;
}
/* Metrics */
.stMetricValue {
    color: #43A363 !important;
    font-weight: bold !important;
}
/* Remove default Streamlit styling */
* { color: inherit !important; }
.stMarkdown p, .stMarkdown div, .stMarkdown span {
    color: #22223B !important;
}
/* --- Custom Selectbox Styling --- */
.stSelectbox {
    background-color: #FFFFFF !important;
    border: 2px solid #E2E8F0 !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.75rem !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
}

/* Label styling (e.g. "🤖 AI Instructions (Optional)") */
.stSelectbox label {
    color: #22223B !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    margin-bottom: 0.5rem !important;
    display: block;
}

/* Selected value text */
.css-1wa3eu0-placeholder, .css-1uccc91-singleValue {
    color: #22223B !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
}

/* Remove default separator line inside dropdown */
.css-1okebmr-indicatorSeparator {
    display: none !important;
}

/* Arrow icon */
.css-tlfecz-indicatorContainer {
    color: #43A363 !important;
}

/* Dropdown menu box */
.css-26l3qy-menu {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    z-index: 9999 !important;
}

/* Dropdown options */
.css-1n7v3ny-option {
    color: #22223B !important;
    padding: 0.6rem 1rem !important;
    font-size: 0.95rem !important;
    border-radius: 6px !important;
    transition: background-color 0.2s ease-in-out;
}

/* Hover and selected option styles */
.css-1n7v3ny-option:hover {
    background-color: #E9F7F0 !important;
    color: #388752 !important;
}
.css-1n7v3ny-option[data-selected="true"] {
    background-color: #B8EFC6 !important;
    color: #22223B !important;
}
/* --- Responsive Design --- */
@media screen and (max-width: 768px) {
    .stRadio > div {
        padding: 1rem !important;
        min-width: unset !important;
        max-width: 100% !important;
    }
    .stSelectbox {
        padding: 0.4rem 0.6rem !important;
    }
    .stButton > button, .stForm button {
        width: 100% !important;
        font-size: 0.95rem !important;
    }
    .stTextInput input, .stTextArea textarea {
        font-size: 0.95rem !important;
        padding: 0.65rem !important;
    }
    h1, h2 {
        font-size: 1.5rem !important;
    }
}

@media screen and (max-width: 480px) {
    .stRadio > div {
        padding: 0.8rem !important;
    }
    .stButton > button, .stForm button {
        padding: 0.6rem 1rem !important;
    }
    h1, h2 {
        font-size: 1.3rem !important;
    }
    h3, h4 {
        font-size: 1.1rem !important;
    }
}
</style>
 """