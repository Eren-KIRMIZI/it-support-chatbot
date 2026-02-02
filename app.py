from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import timedelta
from typing import Optional
import os

from chatbot import process_message
from ticket_service import list_tickets, update_ticket_status, get_ticket_by_id, get_user_tickets
from sla_checker import check_sla_violations
from auth import (
    authenticate_user, 
    create_access_token, 
    get_current_active_user, 
    get_current_admin_user,
    init_default_users,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    User
)

app = FastAPI(title="IT Support Chatbot")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (HTML, CSS, JS)
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Başlangıçta default kullanıcıları oluştur
@app.on_event("startup")
async def startup_event():
    init_default_users()

# ---------- MODELS ----------

class Message(BaseModel):
    message: str

class TicketUpdate(BaseModel):
    status: str

class TicketComment(BaseModel):
    comment: str

# ---------- FRONTEND ROUTES ----------

@app.get("/")
async def root():
    """Ana sayfa - login sayfasına yönlendir"""
    if os.path.exists("frontend/login.html"):
        return FileResponse("frontend/login.html")
    return {
        "status": "online",
        "service": "IT Support Chatbot",
        "version": "2.0",
        "message": "Frontend klasörü bulunamadı. Lütfen frontend/ klasörünü oluşturun."
    }

@app.get("/login.html")
async def login_page():
    if os.path.exists("frontend/login.html"):
        return FileResponse("frontend/login.html")
    raise HTTPException(status_code=404, detail="Login page not found")

@app.get("/user_dashboard.html")
async def user_dashboard():
    if os.path.exists("frontend/user_dashboard.html"):
        return FileResponse("frontend/user_dashboard.html")
    raise HTTPException(status_code=404, detail="User dashboard not found")

@app.get("/admin_dashboard.html")
async def admin_dashboard():
    if os.path.exists("frontend/admin_dashboard.html"):
        return FileResponse("frontend/admin_dashboard.html")
    raise HTTPException(status_code=404, detail="Admin dashboard not found")

# ---------- AUTHENTICATION ----------

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id, "user_type": user.user_type},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": user.user_type,
        "user_id": user.user_id
    }

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# ---------- CHAT (Kullanıcı) ----------

@app.post("/chat")
def chat(msg: Message, current_user: User = Depends(get_current_active_user)):
    return process_message(msg.message, current_user.user_id)

# ---------- TICKETS (Kullanıcı) ----------

@app.get("/my-tickets")
def get_my_tickets(current_user: User = Depends(get_current_active_user)):
    """Kullanıcının kendi ticket'larını listele"""
    return get_user_tickets(current_user.user_id)

@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str, current_user: User = Depends(get_current_active_user)):
    """Belirli bir ticket'ı getir"""
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket bulunamadı")
    
    # Admin değilse sadece kendi ticket'ını görebilir
    if current_user.user_type != "admin" and ticket["user_id"] != current_user.user_id:
        raise HTTPException(status_code=403, detail="Bu ticket'a erişim yetkiniz yok")
    
    return ticket

# ---------- ADMIN DASHBOARD ----------

@app.get("/admin/tickets")
def get_all_tickets(
    status: Optional[str] = None, 
    intent: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Admin: Tüm ticket'ları listele"""
    return list_tickets(status, intent)

@app.put("/admin/tickets/{ticket_id}")
def admin_update_ticket(
    ticket_id: str, 
    data: TicketUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """Admin: Ticket durumunu güncelle"""
    success = update_ticket_status(ticket_id, data.status)
    if success:
        return {"message": f"{ticket_id} güncellendi", "status": data.status}
    raise HTTPException(status_code=404, detail="Ticket bulunamadı")

@app.post("/admin/tickets/{ticket_id}/comment")
def add_comment(
    ticket_id: str,
    data: TicketComment,
    current_user: User = Depends(get_current_admin_user)
):
    """Admin: Ticket'a yorum ekle"""
    from ticket_service import add_ticket_comment
    success = add_ticket_comment(ticket_id, data.comment, current_user.username)
    if success:
        return {"message": "Yorum eklendi"}
    raise HTTPException(status_code=404, detail="Ticket bulunamadı")

# ---------- SLA CHECK (Admin) ----------

@app.post("/admin/sla/check")
def run_sla_check(current_user: User = Depends(get_current_admin_user)):
    """Admin: SLA kontrolü yap"""
    escalated = check_sla_violations()
    return {
        "escalated_count": len(escalated),
        "tickets": escalated
    }

@app.get("/admin/stats")
def get_stats(current_user: User = Depends(get_current_admin_user)):
    """Admin: Dashboard istatistikleri"""
    from ticket_service import get_ticket_stats
    return get_ticket_stats()