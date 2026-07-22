from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from fastapi.testclient import TestClient
import pytest
from models import Users, Todos
from routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:test1234!@localhost/TestTodo'

engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
  db = TestingSessionLocal()
  try:
    yield db
  finally:
    db.close()

def override_get_current_user():
  return {"username": "codingwithrobytest", "id": 1, "user_role": "admin"}

client = TestClient(app)

@pytest.fixture
def test_todo():
  user = Users(
    id=1,
    email="codingwithrobytest@example.com",
    username="codingwithrobytest",
    first_name="Test",
    last_name="User",
    hashed_password="hashedpassword",
    role="admin",
    phone_number="1111111111",
    is_active=True
  )

  todo = Todos(
    id=1,
    title="Learn to code!",
    description="Need to learn everyday!",
    priority=5,
    complete=False,
    owner_id=1
  )

  db = TestingSessionLocal()
  db.add(user)
  db.commit()
  db.add(todo)
  db.commit()
  yield todo
  with engine.connect() as connection:
    connection.execute(text("DELETE FROM todos;"))
    connection.execute(text("DELETE FROM users;"))
    connection.commit()

@pytest.fixture
def test_user():
  user = Users(
    id=1,
    email="codingwithrobytest@example.com",
    username="codingwithrobytest",
    first_name="Roby",
    last_name="Eric",
    hashed_password=bcrypt_context.hash("testpassword"),
    role="admin",
    phone_number="1111111111",
    is_active=True
  )

  db = TestingSessionLocal()
  db.add(user)
  db.commit()
  yield user
  with engine.connect() as connection:
    connection.execute(text("DELETE FROM users;"))
    connection.commit()