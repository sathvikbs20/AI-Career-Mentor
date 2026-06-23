from flask import Flask, render_template, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from google import genai
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from datetime import datetime
import webbrowser
from threading import Timer
import os

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

# -----------------------------
# DATABASE MODELS
# -----------------------------

class Conversation(db.Model):
    __tablename__ = "conversation"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(200),
        nullable=False,
        default="New Chat"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    chats = db.relationship(
        "Chat",
        backref="conversation",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Chat(db.Model):
    __tablename__ = "chat"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversation.id"),
        nullable=False
    )

    user_message = db.Column(
        db.Text,
        nullable=False
    )

    bot_reply = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# -----------------------------
# SYSTEM PROMPT
# -----------------------------

SYSTEM_PROMPT = """
You are an expert AI Career Mentor.

Help students with

• Python
• Java
• AI & Machine Learning
• Data Science
• Web Development
• Resume Building
• Interview Preparation

Always provide clear,
concise,
practical answers.
"""

# Current active conversation
current_conversation = None

# In-memory history
chat_history = []

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# Chat API with Streaming
@app.route("/chat", methods=["POST"])
def chat():

    global current_conversation

    try:

        data = request.get_json()

        user_message = data.get("message", "").strip()

        if not user_message:
            return Response(
                "Please enter a message.",
                mimetype="text/plain"
            )

        # Create first conversation automatically
        if current_conversation is None:

            conversation = Conversation(
                title=user_message[:30]
            )

            db.session.add(conversation)
            db.session.commit()

            current_conversation = conversation.id

            chat_history.clear()

        chat_history.append(
            f"User: {user_message}"
        )

        prompt = f"""
{SYSTEM_PROMPT}

Conversation:

{chr(10).join(chat_history)}

Assistant:
"""
        def generate():

            full_response = ""

            response = client.models.generate_content_stream(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )

            for chunk in response:

                if hasattr(chunk, "text") and chunk.text:

                    full_response += chunk.text

                    yield chunk.text

            chat_history.append(
                f"Assistant: {full_response}"
            )

            message = Chat(
                conversation_id=current_conversation,
                user_message=user_message,
                bot_reply=full_response
            )

            with app.app_context():
                db.session.add(message)
                db.session.commit()

        return Response(
            generate(),
            mimetype="text/plain"
        )

    except Exception as e:

        return Response(
            str(e),
            mimetype="text/plain"
        )
@app.route("/new_chat", methods=["POST"])
def new_chat():

    global current_conversation
    global chat_history

    data = request.get_json()

    title = data.get("title", "New Chat")

    conversation = Conversation(
        title=title
    )

    db.session.add(conversation)
    db.session.commit()

    current_conversation = conversation.id

    chat_history = []

    return jsonify({
        "status": "success",
        "conversation_id": conversation.id
    })
@app.route("/conversations")
def conversations():

    conversations = Conversation.query.order_by(
        Conversation.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at.strftime("%d-%m-%Y %H:%M")
        }
        for c in conversations
    ])
@app.route("/conversation/<int:id>")
def conversation(id):

    global current_conversation
    global chat_history

    current_conversation = id

    messages = Chat.query.filter_by(
        conversation_id=id
    ).order_by(Chat.id.asc()).all()

    chat_history = []

    history = []

    for msg in messages:

        chat_history.append(
            f"User: {msg.user_message}"
        )

        chat_history.append(
            f"Assistant: {msg.bot_reply}"
        )

        history.append({
            "user": msg.user_message,
            "bot": msg.bot_reply
        })

    return jsonify(history)
@app.route("/history")
def history():

    global current_conversation

    if current_conversation is None:
        return jsonify([])

    chats = Chat.query.filter_by(
        conversation_id=current_conversation
    ).order_by(Chat.id.asc()).all()

    return jsonify([
        {
            "user": chat.user_message,
            "bot": chat.bot_reply,
            "time": chat.created_at.strftime("%d-%m-%Y %H:%M")
        }
        for chat in chats
    ])

# Resume Upload
@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    try:

        if "resume" not in request.files:
            return jsonify({
                "reply": "No resume file uploaded."
            })

        file = request.files["resume"]

        if file.filename == "":
            return jsonify({
                "reply": "Please select a PDF file."
            })

        if not file.filename.lower().endswith(".pdf"):
            return jsonify({
                "reply": "Only PDF files are allowed."
            })

        os.makedirs("uploads", exist_ok=True)

        filepath = os.path.join(
            "uploads",
            file.filename
        )

        file.save(filepath)

        # Extract PDF text
        resume_text = ""

        pdf = PdfReader(filepath)

        for page in pdf.pages:

            text = page.extract_text()

            if text:
                resume_text += text + "\n"

        # Delete uploaded file
        try:
            os.remove(filepath)
        except:
            pass

        if not resume_text.strip():
            return jsonify({
                "reply": "Could not extract text from PDF."
            })

        prompt = f"""
Analyze this resume and provide:

1. ATS Score (/100)
2. Skills Found
3. Strengths
4. Weaknesses
5. Improvement Suggestions
6. Suitable Career Roles
7. Interview Preparation Tips
8. Missing Keywords
9. Resume Rating

Resume:

{resume_text[:10000]}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        return jsonify({
            "reply": response.text
        })

    except Exception as e:

        print("Resume Error:", e)

        return jsonify({
            "reply": f"⚠️ Resume analysis failed: {str(e)}"
        })

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    Timer(1, open_browser).start()

    app.run(debug=True, use_reloader=False)