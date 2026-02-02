from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from db import db

# JWT ayarları
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 saat

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

users_collection = db["users"]

# ---------- MODELS ----------

class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    user_type: Optional[str] = None

class User(BaseModel):
    user_id: str
    username: str
    email: str
    user_type: str  # "user" veya "admin"
    full_name: Optional[str] = None
    department: Optional[str] = None
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

# ---------- PASSWORD ----------

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# ---------- USER OPERATIONS ----------

def get_user(username: str) -> Optional[UserInDB]:
    user_doc = users_collection.find_one({"username": username})
    if user_doc:
        return UserInDB(**user_doc)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulaması başarısız",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, user_type=user_type)
    except JWTError:
        raise credentials_exception
    
    user = users_collection.find_one({"user_id": token_data.user_id})
    if user is None:
        raise credentials_exception
    return User(**user)

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için admin yetkisi gerekiyor"
        )
    return current_user

# ---------- INIT DEFAULT USERS ----------

def init_default_users():
    """Varsayılan kullanıcıları oluştur"""
    
    # Admin kullanıcısı
    if not users_collection.find_one({"username": "admin"}):
        admin_user = {
            "user_id": "admin_001",
            "username": "admin",
            "email": "admin@company.com",
            "full_name": "Admin User",
            "department": "IT",
            "user_type": "admin",
            "hashed_password": get_password_hash("admin123"),
            "disabled": False,
            "created_at": datetime.utcnow()
        }
        users_collection.insert_one(admin_user)
        print("Admin kullanıcısı oluşturuldu (username: admin, password: admin123)")
    
    # Test kullanıcısı
    if not users_collection.find_one({"username": "user1"}):
        test_user = {
            "user_id": "user_001",
            "username": "user1",
            "email": "user1@company.com",
            "full_name": "Test User",
            "department": "Sales",
            "user_type": "user",
            "hashed_password": get_password_hash("user123"),
            "disabled": False,
            "created_at": datetime.utcnow()
        }
        users_collection.insert_one(test_user)
        print("Test kullanıcısı oluşturuldu (username: user1, password: user123)")