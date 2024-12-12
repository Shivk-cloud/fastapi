from fastapi import FastAPI, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal

app = FastAPI()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

class UserSchema(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        orm_mode = True

class UserCreateSchema(BaseModel):
    email: str
    is_active: bool

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

@app.post("/users", response_model=UserSchema)
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    u = User(email=user.email, is_active=user.is_active)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u



@app.get("/users", response_model=List[UserSchema])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)