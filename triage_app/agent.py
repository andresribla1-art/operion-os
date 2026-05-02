import os
import re
from groq import Groq
from knowledge_base import get_system_prompt

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

INTENT_LABELS = {
    "faq":          "FAQ",
    "pricing":      "Pricing",
    "trial":        "Trial",
    "signup":       "Signup",
    "corporate":    "Corporate",
    "cancellation": "Cancellation",
    "complaint":    "Complaint",
    "escalate":     "Unclear",
}

CHANNEL_NOTES = {
    "instagram": "\nNote: Instagram DM — keep response concise, max 150 words.",
    "whatsapp":  "\nNote: WhatsApp message — slightly longer responses are fine.",
}

GERMAN_MARKERS = re.compile(
    r'\b(ich|bitte|danke|hallo|guten|wie|was|wann|preis|kosten|kostet|'
    r'öffnung|mitglied|probe|training|können|haben|ist|sind|der|die|das|und|'
    r'möchte|würde|bitte|schon|noch|auch|mal)\b',
    re.IGNORECASE
)

INTENTS = [
    ("cancellation", r'\b(kündigung|kündigen|cancel|abmelden|austritt|kündige)\b'),
    ("complaint",    r'\b(beschwerde|complaint|problem|unzufrieden|disappointed|schlecht|terrible)\b'),
    ("corporate",    r'\b(audi|man\b|thi|student|studierende|corporate|mitarbeiter|firmen)\b'),
    ("trial",        r'\b(probe|trial|probetraining|kostenlos testen|try|probezeit|schnuppern)\b'),
    ("signup",       r'\b(anmelden|sign up|join|mitglied werden|beitreten|registrier)\b'),
    ("pricing",      r'\b(preis|kosten|kostet|price|cost|how much|tarif|plan|rate|was kostet|mitgliedschaft|gebühr|euro|€)\b'),
]

def detect_language(text: str) -> str:
    return "de" if len(GERMAN_MARKERS.findall(text)) >= 2 else "en"

def classify_intent(text: str) -> str:
    for intent, pattern in INTENTS:
        if re.search(pattern, text, re.IGNORECASE):
            return intent
    return "faq"

def generate_response(message: str, channel: str, history: list = None) -> dict:
    if history is None:
        history = []
    language = detect_language(message)
    intent = classify_intent(message)
    system_prompt = get_system_prompt(language) + CHANNEL_NOTES.get(channel, "")

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    completion = client.chat.completions.create(
        model=MODEL,
        max_tokens=512,
        timeout=10,
        messages=messages
    )

    return {
        "response":     completion.choices[0].message.content,
        "language":     language,
        "intent":       intent,
        "intent_label": INTENT_LABELS.get(intent, intent),
        "channel":      channel,
    }
