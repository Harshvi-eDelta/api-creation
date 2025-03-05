from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal, get_db
import bcrypt


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class PersonBase(BaseModel) :
    name:str    
    email:str
    password:str

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()  # Generate salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)  
    return hashed_password.decode('utf-8')  

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@app.post('/addperson',status_code = status.HTTP_201_CREATED)
def add_person(new_person : PersonBase,db : Session = Depends(get_db)) :
    hashed_password = hash_password(new_person.password)
    personData = models.Person(name=new_person.name,email=new_person.email,password=hashed_password)
    db.add(personData)
    db.commit()
    db.refresh(personData)
    return {"Person added" : personData}

@app.get('/getperson/{id}')
def get_person(id:int,db:Session=Depends(get_db)):
    per = db.query(models.Person).filter(models.Person.id == id).first()
    if not per :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Person with id {id} not found")
    return {"Details" : per}

#delete post
@app.delete("/deleteperson/{id}")
async def delete_person(id: int, db: Session = Depends(get_db)):
    del_per = db.query(models.Person).filter(models.Person.id == id)

    if del_per.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Person with id {id} does not exist")
    del_per.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#update post
@app.put("/updateperson/{id}")
async def update_person(id: int, new_post: PersonBase, db: Session = Depends(get_db)):
    query = db.query(models.Person).filter(models.Person.id == id)
    per1 = query.first()

    if per1 == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Person with id {id} does not exist")
    if new_person.password:
        hashed_password = hash_password(new_person.password)
        new_person.password = hashed_password
    query.update(new_post.dict(), synchronize_session=False)
    db.commit()
    return {"Data": query.first()}    