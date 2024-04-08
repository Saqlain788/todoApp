from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from todo import settings
from contextlib import asynccontextmanager
from typing import Annotated, Optional

class ToDo(SQLModel, table=True):
    id: Optional[int] = Field (default=None, primary_key=True)
    content: str = Field(index=True)
    is_completeed: bool = Field(False)

conection_string = str(settings.DATABASE_URL).replace(
    'postgresql', "postgresql+psycopg")

engine = create_engine(
    conection_string, connect_args={"sslmode": "require"}, pool_recycle=300
    )
def create_db_table():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Generating table")
    create_db_table ()
    print ("Ending table")
    yield
   

app  = FastAPI(lifespan = life_span)

def get_session():
    with Session(engine) as session:
        yield session



@app.get("/")
def read_route():
    return {"message": "Hello Class Batch47-Lahore"}

# Create Todo 
@app.post("/todos/", response_model = ToDo)
def create_todo(todo: ToDo, session: Annotated[Session, Depends(get_session)]):
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

# Get all todo list
@app.get("/todos/", response_model = list[ToDo])
def all_todos(session: Annotated[Session, Depends(get_session)]):
         query = select(ToDo)
         todos = session.exec(query).all()
         if todos:
            return todos
         else:
            raise HTTPException(status_code=404, detail="Todo not found")

# Get a single Todo

@app.get("/todos/{id}", response_model = ToDo)
def single_todo (id: int, session: Annotated[Session, Depends(get_session)]):
     query = select(ToDo)
     todo = session.exec(query.where(ToDo.id == id)).first()
     if todo:
        return todo
     else: 
          raise HTTPException(status_code=404, detail="Todo not found")
     
# Update Todo 
@app.put('/todos/{id}', response_model=ToDo)
def edit_todo(id: int, todo: ToDo, session: Annotated[Session, Depends(get_session)]):
    existing_todo = session.exec(select(ToDo).where(ToDo.id == id)).first()
    if existing_todo:
        existing_todo.content = todo.content
        existing_todo.is_completeed = todo.is_completeed
        session.add(existing_todo)
        session.commit()
        session.refresh(existing_todo)
        return existing_todo
    else:
        raise HTTPException(status_code=404, detail="No todo found")
    
# Delete Todo
@app.delete("/todos/{id}")
async def removed_todo(id:int, session:Annotated[Session, Depends(get_session)]):
    todo = session.get(ToDo, id)
    if todo:
         session.delete(todo)
         session.commit()
         
         return {"message": "todo sucessfully deleted"}
    else:
         raise HTTPException(status_code=404, detail="Todo not found")
