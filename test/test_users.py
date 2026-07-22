from .utils import *
from database import get_db
from routers.auth import get_current_user
from fastapi import status
from routers.auth import bcrypt_context

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
  response = client.get("/user")
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == {
    "id": 1,
    "email": "codingwithrobytest@example.com",
    "username": "codingwithrobytest",
    "first_name": "Roby",
    "last_name": "Eric",
    "hashed_password": test_user.hashed_password,
    "role": "admin",
    "phone_number": "1111111111",
    "is_active": True
  }

def test_change_password_success(test_user):
  response = client.put("/user/password", json={
    "password": "testpassword",
    "new_password": "newtestpassword"
  })
  assert response.status_code == status.HTTP_204_NO_CONTENT

  db = TestingSessionLocal()
  model = db.query(Users).filter(Users.id == 1).first()
  assert bcrypt_context.verify("newtestpassword", model.hashed_password)

def test_change_password_invalid_current_password(test_user):
  response = client.put("/user/password", json={
    "password": "invalidpassword",
    "new_password": "newtestpassword"
  })
  assert response.status_code == status.HTTP_401_UNAUTHORIZED
  assert response.json() == {
    "detail": "Error on password change"
  }

def change_phone_number_success(test_user):
  response = client.put("/user/phonenumber/666-666-6666")
  assert response.status_code == status.HTTP_204_NO_CONTENT

  db = TestingSessionLocal()
  model = db.query(Users).filter(Users.id == 1).first()
  assert model.phone_number == "666-666-6666"