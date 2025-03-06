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
import base64

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class PersonBase(BaseModel) :
    name:str    
    email:str
    password:str

def encode_password(password: str) -> str:
    encoded = base64.b64encode(password.encode('utf-8'))
    return encoded.decode('utf-8')

def decode_password(encoded_password: str) -> str:
    padding = len(encoded_password) % 4
    if padding != 0:
        encoded_password += '=' * (4 - padding)
    #decoded = base64.b64decode(encoded_password.encode('utf-8'))
    #return decoded.decode('utf-8')
    try:
        # Attempt to base64 decode and decode it as UTF-8
        decoded_bytes = base64.b64decode(encoded_password.encode('utf-8'))
        # If you expect it to be a UTF-8 string, decode it:
        return decoded_bytes.decode('utf-8')  # or you could just return the raw bytes if it's binary
    except UnicodeDecodeError:
        # If it fails to decode as UTF-8, return the raw bytes (or handle the error in another way)
        return decoded_bytes

@app.post('/addperson',status_code = status.HTTP_201_CREATED)
def add_person(new_person : PersonBase,db : Session = Depends(get_db)) :
    #personData = models.Person(**new_person.dict())

    encode_pwd = encode_password(new_person.password)
    personData = models.Person(name = new_person.name,email = new_person.email,password = encode_pwd)

    db.add(personData)
    db.commit()
    db.refresh(personData)
    return {"Person added" : personData}

@app.get('/getperson/{id}')
def get_person(id:int,db:Session=Depends(get_db)):
    per = db.query(models.Person).filter(models.Person.id == id).first()
    if not per :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Person with id {id} not found")
    decoded_pwd = decode_password(per.password)
    #return {"Details" : per}
    return {"Details": {"name": per.name, "email": per.email, "password": decoded_pwd}}

'''@app.get('/getall')
def get_all(db:Session = Depends(get_db)) :
    per = db.query(models.Person).all()
    if not per :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No person")
    decode_all_pwd = []
    for p in per :
        decoded_pwd = decode_password(p.password)
        decode_all_pwd.append({"name": p.name, "email": p.email, "password": decoded_pwd})
    return {"Details" : decode_all_pwd}'''

@app.get('/getall')
def get_all(db: Session = Depends(get_db)):
    per = db.query(models.Person).all()
    if not per:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No person found")
    decode_all_pwd = []
    for p in per:
        decoded_pwd = decode_password(p.password)  # Decode the password here
        if isinstance(decoded_pwd, bytes):
            # Handle the case where the password is binary data and not a UTF-8 string
            decoded_pwd = decoded_pwd.decode('UTF-8','ignore')  # You can also decide how to handle this case
        decode_all_pwd.append({"name": p.name, "email": p.email, "password": decoded_pwd})  # Append the decoded password
    return {"Details": decode_all_pwd}


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
async def update_person(id: int, new_per: PersonBase, db: Session = Depends(get_db)):
    query = db.query(models.Person).filter(models.Person.id == id)
    per1 = query.first()

    if per1 == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Person with id {id} does not exist")
    #query.update(new_per.dict(), synchronize_session=False)

    new_password = encode_password(new_per.password) if new_per.password else per1.password
    query.update({
        models.Person.name: new_per.name,models.Person.email: new_per.email,models.Person.password: new_password}, synchronize_session=False)

    db.commit()
    return {"Data": query.first()}    