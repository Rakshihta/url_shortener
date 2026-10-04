from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import secrets, string
from datetime import date

from database import SessionLocal, engine, Base, get_db
import models, auth_utils

Base.metadata.create_all(bind = engine)
app = FastAPI()

class UserCreate(BaseModel):
    email : str
    password : str

class UserLogin(BaseModel):
    email : str
    password : str


@app.post("/signup")
def signup(user: UserCreate,db: Session = Depends(get_db)):

    exist_user = db.query(models.User).filter(models.User.email == user.email).first()
    if exist_user:
        raise HTTPException(status_code=400, detail="Email already registered")


    hashed_password = auth_utils.hash_password(user.password)


    new_user = models.User(email = user.email,hashed_password= hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id" : new_user.id,
        "email" : new_user.email
    }

@app.post("/login")
def login(user: UserLogin,db : Session = Depends(get_db)):

    current_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    validate = auth_utils.verify_password(user.password,current_user.hashed_password)
    if(validate):
        token = auth_utils.create_access_token({"sub": str(current_user.id)})
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": token, "token_type": "bearer"}


class LinkCreate(BaseModel):
    long_url: str

def generate_code(length=6):
    character = string.ascii_letters + string.digits
    return ''.join(secrets.choice(character) for _ in range(6))


@app.post("/links")
def create_link(link: LinkCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth_utils.get_current_user_optional)):
    short_code = generate_code()

    #this allows the user to use the website even without logging in
    if current_user:
        owner_id = current_user.id
    else:
        owner_id = None
    
    
    new_link = models.Link(
        short_code = short_code,
        long_url = link.long_url,
        owner_id = owner_id
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)


    return {
        "short_code" : short_code,
        "long_url" : link.long_url,
        "owner_id" : owner_id
    }


    