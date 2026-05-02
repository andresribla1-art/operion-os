import os
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from agent import generate_response

app = Flask(__name__)
DB_PATH = "logs.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                channel TEXT,
                language TEXT,
                intent TEXT,
                message_length INTEGER,
                escalated INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                channel TEXT,
                label TEXT,
                created_at TEXT,
                last_message TEXT,
                last_intent TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                intent TEXT,
                language TEXT,
                timestamp TEXT
            )
        """)

def log_interaction(channel, language, intent, message_length):
    escalated = 1 if intent in ("cancellation", "complaint", "escalate") else 0
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO interactions (timestamp, channel, language, intent, message_length, escalated) VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), channel, language, intent, message_length, escalated)
        )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/conversations", methods=["GET"])
def list_conversations():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT id, channel, label, created_at, last_message, last_intent
            FROM conversations ORDER BY created_at DESC
        """).fetchall()
    return jsonify([{
        "id": r[0], "channel": r[1], "label": r[2],
        "created_at": r[3], "last_message": r[4], "last_intent": r[5]
    } for r in rows])

@app.route("/conversations", methods=["POST"])
def create_conversation():
    data = request.get_json()
    channel = data.get("channel", "instagram")
    conv_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO conversations (id, channel, label, created_at, last_message, last_intent) VALUES (?, ?, ?, ?, ?, ?)",
            (conv_id, channel, "Nueva conversación", now, "", "")
        )
    return jsonify({
        "id": conv_id, "channel": channel, "label": "Nueva conversación",
        "created_at": now, "last_message": "", "last_intent": ""
    })

@app.route("/conversations/<conv_id>", methods=["DELETE"])
def delete_conversation(conv_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    return jsonify({"ok": True})

@app.route("/conversations/<conv_id>/messages", methods=["GET"])
def get_messages(conv_id):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT role, content, intent, language, timestamp
            FROM messages WHERE conversation_id = ?
            ORDER BY id ASC
        """, (conv_id,)).fetchall()
    return jsonify([{
        "role": r[0], "content": r[1], "intent": r[2],
        "language": r[3], "timestamp": r[4]
    } for r in rows])

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    message = (data.get("message") or "").strip()
    conv_id = data.get("conversation_id")

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400
    if not conv_id:
        return jsonify({"error": "conversation_id required"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        conv = conn.execute(
            "SELECT channel, label FROM conversations WHERE id = ?", (conv_id,)
        ).fetchone()
        if not conv:
            return jsonify({"error": "Conversation not found"}), 404
        channel, current_label = conv[0], conv[1]

        history_rows = conn.execute("""
            SELECT role, content FROM messages
            WHERE conversation_id = ? ORDER BY id ASC
        """, (conv_id,)).fetchall()

    # Limit to last 20 messages to avoid token overflow
    history = [{"role": r[0], "content": r[1]} for r in history_rows[-20:]]
    result = generate_response(message, channel, history)

    now = datetime.utcnow().isoformat()
    snippet = message[:55] + ("..." if len(message) > 55 else "")

    if current_label == "Nueva conversación":
        new_label = f"{result['intent_label']} · {result['language'].upper()}"
    else:
        new_label = current_label

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, intent, language, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (conv_id, "user", message, result["intent"], result["language"], now)
        )
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, intent, language, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (conv_id, "assistant", result["response"], result["intent"], result["language"], now)
        )
        conn.execute(
            "UPDATE conversations SET last_message=?, last_intent=?, label=? WHERE id=?",
            (snippet, result["intent"], new_label, conv_id)
        )

    log_interaction(channel, result["language"], result["intent"], len(message))
    result["new_label"] = new_label
    return jsonify(result)

@app.route("/stats")
def stats():
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("""
            SELECT COUNT(*) as total, SUM(escalated) as escalated,
                   COUNT(CASE WHEN language='de' THEN 1 END) as german,
                   COUNT(CASE WHEN language='en' THEN 1 END) as english
            FROM interactions
        """).fetchone()
    return jsonify({
        "total": row[0], "escalated": row[1],
        "german": row[2], "english": row[3]
    })

if __name__ == "__main__":
    init_db()
    print("\n OPERION TRIAGE - Clever Fit Ingolstadt")
    print(" Open in browser: http://localhost:5000\n")
    app.run(debug=False, port=5000)
