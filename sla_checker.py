from datetime import datetime
from ticket_service import tickets_collection

def check_sla_violations():
    now = datetime.utcnow()

    overdue_tickets = tickets_collection.find({
        "status": "open",
        "sla_deadline": {"$lt": now},
        "escalated": False
    })

    escalated = []

    for ticket in overdue_tickets:
        tickets_collection.update_one(
            {"ticket_id": ticket["ticket_id"]},
            {"$set": {
                "status": "escalated",
                "escalated": True,
                "escalated_at": now
            }}
        )
        escalated.append(ticket["ticket_id"])

    return escalated
