from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
data = []

class Book(BaseModel):
    id : int
    title : str

@app.post('/book')
def add_book(book : Book):
    data.append(book.dict())
    return data

@app.get('/list')
def get_books() :
    return data
    
@app.put('/book/{id}')
def update_book(id:int,book : Book):
    data[id-1] = book   
    return data

@app.delete('/book/{id}')
def delete_book(id:int):
    data.pop(id-1)
    return data

