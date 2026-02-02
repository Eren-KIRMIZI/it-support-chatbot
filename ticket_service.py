from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient("mongodb://localhost:27017")
db = client["it_support"]
tickets_collection = db["tickets"]

# ---- RULE ENGINE ----

INTENT_RULES = {
    "vpn_issue":      {"severity": "high",     "priority": "P2"},
    "network_issue":  {"severity": "critical", "priority": "P1"},
    "email_issue":    {"severity": "medium",   "priority": "P3"},
    "ticket_request": {"severity": "medium",   "priority": "P3"},
    "password_reset": {"severity": "low",      "priority": "P4"},
    "unknown":        {"severity": "low",      "priority": "P4"}
}

SLA_RULES = {
    "P1": timedelta(hours=1),
    "P2": timedelta(hours=4),
    "P3": timedelta(hours=24),
    "P4": timedelta(hours=72)
}

# ---- HELPERS ----

def generate_ticket_id():
    last = tickets_collection.find_one(sort=[("created_at", -1)])
    if not last:
        return "IT-1001"
    last_id = int(last["ticket_id"].split("-")[1])
    return f"IT-{last_id + 1}"

# ---- CORE ----

def create_ticket(user_id: str, issue: str, intent: str):
    ticket_id = generate_ticket_id()
    rule = INTENT_RULES.get(intent, INTENT_RULES["unknown"])

    priority = rule["priority"]
    created_at = datetime.utcnow()
    sla_deadline = created_at + SLA_RULES[priority]

    ticket = {
        "ticket_id": ticket_id,
        "user_id": user_id,
        "issue": issue,
        "intent": intent,
        "severity": rule["severity"],
        "priority": priority,
        "status": "open",
        "escalated": False,
        "created_at": created_at,
        "sla_deadline": sla_deadline,
        "comments": []
    }

    tickets_collection.insert_one(ticket)
    print("DB INSERTED:", ticket)

    return ticket_id

def list_tickets(status: str = None, intent: str = None):
    query = {}
    if status:
        query["status"] = status
    if intent:
        query["intent"] = intent

    return list(tickets_collection.find(query, {"_id": 0}).sort("created_at", -1))

def get_user_tickets(user_id: str):
    """Kullanıcının kendi ticket'larını getir"""
    return list(tickets_collection.find(
        {"user_id": user_id}, 
        {"_id": 0}
    ).sort("created_at", -1))

def get_ticket_by_id(ticket_id: str):
    """ID'ye göre ticket getir"""
    return tickets_collection.find_one({"ticket_id": ticket_id}, {"_id": 0})

def update_ticket_status(ticket_id: str, status: str):
    result = tickets_collection.update_one(
        {"ticket_id": ticket_id},
        {"$set": {
            "status": status,
            "updated_at": datetime.utcnow()
        }}
    )
    return result.modified_count > 0

def add_ticket_comment(ticket_id: str, comment: str, author: str):
    """Ticket'a yorum ekle"""
    comment_obj = {
        "author": author,
        "comment": comment,
        "timestamp": datetime.utcnow()
    }
    
    result = tickets_collection.update_one(
        {"ticket_id": ticket_id},
        {"$push": {"comments": comment_obj}}
    )
    return result.modified_count > 0

def get_ticket_stats():
    """Dashboard için istatistikler"""
    total = tickets_collection.count_documents({})
    open_tickets = tickets_collection.count_documents({"status": "open"})
    in_progress = tickets_collection.count_documents({"status": "in_progress"})
    closed = tickets_collection.count_documents({"status": "closed"})
    escalated = tickets_collection.count_documents({"escalated": True})
    
    # Priority dağılımı
    p1 = tickets_collection.count_documents({"priority": "P1"})
    p2 = tickets_collection.count_documents({"priority": "P2"})
    p3 = tickets_collection.count_documents({"priority": "P3"})
    p4 = tickets_collection.count_documents({"priority": "P4"})
    
    # SLA ihlali olanlar
    now = datetime.utcnow()
    sla_breached = tickets_collection.count_documents({
        "status": {"$in": ["open", "in_progress"]},
        "sla_deadline": {"$lt": now}
    })
    
    return {
        "total_tickets": total,
        "open": open_tickets,
        "in_progress": in_progress,
        "closed": closed,
        "escalated": escalated,
        "sla_breached": sla_breached,
        "priority_distribution": {
            "P1": p1,
            "P2": p2,
            "P3": p3,
            "P4": p4
        }
    }