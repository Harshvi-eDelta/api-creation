from fastapi import FastAPI
#import random
from fastapi.params import Body
app = FastAPI()
posts = []

'''@app.get('/')
async def root() :
    return {"Information" : "This is an example of FastAPI", "Data" : 0}

@app.get('/random')
async def random_number() :
    rn:int = random.randint(0,100)
    return {"number" : rn, "limit" : 100}

@app.get('/random_num{limit}')
async def random_gen(limit:int):
    rn:int = random.randint(0,limit)
    return {"number" : rn, "limit" : limit}'''

# GET Method
@app.get('/')
async def root() :
    return {"Message",f"{posts}"}

# If we want to access data with specific number
@app.get('/{number}')
async def root(number:int) :
    return {"Message",f"{posts[number]}"}

#POST Method
@app.post('/createpost')
async def create_post(info : dict = Body(...)) :
    posts.append(info)
    #print(posts)
    return {f"POST created, {info['title']},{info['message']}"}
