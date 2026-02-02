from intent_model import IntentClassifier
from faq_engine import FAQEngine
from ticket_service import create_ticket

intent_classifier = IntentClassifier()
faq_engine = FAQEngine()

# Cevap verilse bile ticket açılacak intent'ler
AUTO_TICKET_INTENTS = {
    "vpn_issue",
    "network_issue",
    "email_issue"
}

def process_message(message: str, user_id: str):
    # Intent tespiti
    try:
        intent = intent_classifier.predict(message)
        intent = intent.strip().lower()
    except Exception as e:
        print("INTENT ERROR:", e)
        intent = "unknown"

    # FAQ / KB araması
    try:
        answer = faq_engine.search(message)
    except Exception as e:
        print("FAQ ERROR:", e)
        answer = None

    # Ticket kararı
    ticket_created = False
    ticket_id = None

    should_create_ticket = (
        intent == "ticket_request"
        or intent in AUTO_TICKET_INTENTS
    )

    if should_create_ticket:
        try:
            ticket_id = create_ticket(
                user_id=user_id,
                issue=message,
                intent=intent
            )
            ticket_created = True
            print(f"TICKET CREATED → {ticket_id} ({intent})")
        except Exception as e:
            print("TICKET CREATE ERROR:", e)

    # Response
    if answer:
        return {
            "response": answer,
            "intent": intent,
            "ticket_created": ticket_created,
            "ticket_id": ticket_id
        }

    return {
        "response": "Sorununuz IT ekibine iletildi.",
        "intent": intent,
        "ticket_created": ticket_created,
        "ticket_id": ticket_id
    }
