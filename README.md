# AI Career Mentor Chatbot

## Overview

AI Career Mentor is an LLM-powered chatbot built using **Python, Flask, Google Gemini API, SQLite, HTML, CSS, and JavaScript**. The chatbot helps students with career guidance, interview preparation, resume analysis, programming questions, and AI-related topics.

This project was developed as part of the **Build Your Own LLM Powered AI Chatbot** challenge.

---

# Features

* AI-powered chatbot using Google Gemini
* Streaming AI responses
* Multi-turn conversations
* Conversation history
* New Chat functionality
* Resume PDF upload and analysis
* SQLite database for storing chats
* Markdown formatted responses
* Modern responsive user interface

---

# Technologies Used

* Python
* Flask
* Google Gemini API
* SQLite
* HTML5
* CSS3
* JavaScript
* PyPDF2
* Flask-SQLAlchemy

---

# Project Structure

```
AI_Career_Mentor/
│
├── app.py
├── requirements.txt
├── .env
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── uploads/
│
├── instance/
│   └── chat.db
│
└── README.md
```

---

# Installation

## 1. Clone the Repository

```
git clone https://github.com/yourusername/AI_Career_Mentor.git
```

## 2. Navigate to the Project Folder

```
cd AI_Career_Mentor
```

## 3. Create a Virtual Environment

Windows

```
python -m venv venv
```

Activate the virtual environment

```
venv\Scripts\activate
```

## 4. Install Dependencies

```
pip install -r requirements.txt
```

## 5. Configure Environment Variables

Create a `.env` file.

Add your Gemini API key:

```
GEMINI_API_KEY=YOUR_API_KEY
```

## 6. Run the Application

```
python app.py
```

The application will automatically open in your browser.

---

# How to Use

1. Launch the application.
2. Click **New Chat** to start a conversation.
3. Ask career-related or programming questions.
4. Upload a PDF resume for AI analysis.
5. View previous conversations from the sidebar.
6. Clear the chat when required.

---

# Sample Questions

* How can I become a Python Developer?
* Explain Machine Learning.
* Help me prepare for an interview.
* Review my resume.
* Suggest projects for beginners.

---

# Future Improvements

* User Authentication
* Voice Input
* Export Chat
* AI Generated Conversation Titles
* Dark/Light Theme

---

# Author

**Sathvik B S**

MCA Student

Presidency University, Bengaluru

[sathvikbs20@gmail.com](mailto:sathvikbs20@gmail.com)

---

# License

This project is developed for educational and learning purposes.
