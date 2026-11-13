from fastapi import FastAPI, Depends, HTTPException, status, Form, APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# Configuración y constantes
SECRET_KEY = os.getenv("AUTH_SECRET", "secret_dev_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 días

DATABASE_URL = os.getenv("DATABASE_URL")

# Intentar conectar a PostgreSQL, fallback a SQLite
try:
    engine = create_engine(DATABASE_URL, echo=False, future=True)
    # Probar conexión simple
    with engine.connect() as conn:
        conn.execute("SELECT 1")
except Exception:
    # Fallback a SQLite local
    DATABASE_URL = "sqlite:///./app.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()

# Modelos SQLAlchemy
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True

class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ItemOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Seguridad y autenticación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependencias
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: str = Depends(lambda request: request.headers.get("Authorization", "").replace("Bearer ", "")), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# FastAPI app y router
app = FastAPI(title="API YERUZZA STUDIO")

# Prefijo /api para todos los endpoints
api_router = APIRouter(prefix="/api")

# CORS (opcional, ajustar según necesidades)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints públicos
@api_router.get("/health", tags=["Salud"])
def health_check():
    return {"status": "ok"}

@api_router.post("/auth/register", tags=["Autenticación"])
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "Usuario creado correctamente"}

@api_router.post("/auth/login", response_model=Token, tags=["Autenticación"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/auth/me", response_model=UserOut, tags=["Autenticación"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Endpoints CRUD protegidos para Items
@api_router.post("/items/", response_model=ItemOut, tags=["Items"])
async def create_item(item: ItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = Item(title=item.title, description=item.description, owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@api_router.get("/items/", response_model=List[ItemOut], tags=["Items"])
async def read_items(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(Item).filter(Item.owner_id == current_user.id).offset(skip).limit(limit).all()
    return items

@api_router.get("/items/{item_id}", response_model=ItemOut, tags=["Items"])
async def read_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item

@api_router.put("/items/{item_id}", response_model=ItemOut, tags=["Items"])
async def update_item(item_id: int, item_update: ItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    item.title = item_update.title
    item.description = item_update.description
    db.commit()
    db.refresh(item)
    return item

@api_router.delete("/items/{item_id}", status_code=204, tags=["Items"])
async def delete_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    db.delete(item)
    db.commit()
    return JSONResponse(status_code=204, content=None)

# Incluir router en la app
app.include_router(api_router)