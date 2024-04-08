from fastapi.testclient import TestClient
from fastapi import FastAPI
from todo import settings
from sqlmodel import SQLModel, create_engine, Session
from todo.main import app, get_session
import pytest

connection_string = str(settings.TEST_DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")

engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)

# Refactor with pytest fixture

@pytest.fixture(scope="module", autouse=True)
def get_db_session():
    SQLModel.metadata.create_all(engine)
    yield Session(engine)

@pytest.fixture(scope='function')
def test_app(get_db_session):
    def test_session():
        yield get_db_session
    app.dependency_overrides[get_session] = test_session
    with TestClient(app=app) as client:
        yield client

# Test 1: Root Test
def test_read_route():
    client = TestClient(app=app)
    response = client.get('/')
    data = response.json()
    assert response.status_code == 200
    assert data == {"message": "Hello Class Batch47-Lahore"}

# Test 2: Post Test
def test_create_todo(test_app): 
    # SQLModel.metadata.create_all(engine)  
    # with Session(engine) as session:  
    #     def get_session_override():  
    #             return session  
    #     app.dependency_overrides[get_session] = get_session_override 
    #     client = TestClient(app=app)
        test_todo = {"content":"Sleeping", "is_completeed":False}
        response = test_app.post("/todos/",
            json=test_todo
        )
        data = response.json()
        assert response.status_code == 200
        assert data["content"] == test_todo["content"]

# Test 3: Get all todos
def test_all_todos(test_app):
    # SQLModel.metadata.create_all(engine)  
    # with Session(engine) as session:  
    #     def get_session_override():  
    #             return session  
    #     app.dependency_overrides[get_session] = get_session_override 
    #     client = TestClient(app=app)
        test_todo = {"content":"get all todos", "is_completeed":False}
        response = test_app.post('/todos/', json=test_todo)
        data = response.json()

        response = test_app.get("/todos/")
        new_todo = response.json()[-1]
        assert response.status_code == 200
        assert new_todo["content"] == test_todo["content"]

# Test 4: Get single todo Test
def test_single_todo(test_app):
    # SQLModel.metadata.create_all(engine)  
    # with Session(engine) as session:  
    #     def get_session_override():  
    #             return session  
    #     app.dependency_overrides[get_session] = get_session_override 
    #     client = TestClient(app=app)
        
        test_todo = {"content":"get single todo test", "is_completeed":False}
        response = test_app.post('/todos/', json=test_todo)
        todo_id = response.json()["id"]

        response = test_app.get(f"/todos/{todo_id}")
        data = response.json()
        assert response.status_code == 200
        assert data["content"] == test_todo["content"]

# Test 5: Update Todo Test
def test_updated_todo(test_app):
    #  SQLModel.metadata.create_all(engine)
    #  with Session(engine) as session:
    #      def get_session_override():
    #          return session
    #      app.dependency_overrides[get_session] = get_session_override
    #      client = TestClient(app=app)
         
        test_todo = {"content":"edit todo test", "is_completed":False}
        response = test_app.post('/todos/',json=test_todo)
        todo_id = response.json()["id"]

        edited_todo = {"content":"We have edited this", "is_completed":False}
        response = test_app.put(f'/todos/{todo_id}',json=edited_todo)
        data = response.json()
        assert response.status_code == 200
        assert data["content"] == edited_todo["content"]

# Test 6: Delete Todo
def test_removed_todo(test_app):
    #  SQLModel.metadata.create_all(engine)
    #  with Session(engine) as session:
    #      def get_session_override():
    #          return session
    #      app.dependency_overrides[get_session] = get_session_override
    #      client = TestClient(app=app)

         test_todo = {"content":"delete single todo test", "is_completed":False}
         response = test_app.post('/todos/', json=test_todo)
         todo_id = response.json()["id"]

         response = test_app.delete(f"/todos/{todo_id}")
         data = response.json()
         assert response.status_code == 200
         assert data["message"] == "todo sucessfully deleted"