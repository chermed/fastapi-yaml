from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Extra

from fastapi_yaml import YamlRoute

app = FastAPI()
app.router.route_class = YamlRoute


class Person(BaseModel, extra='forbid'):
    name: str
    age: int


@app.post("/person")
def person(person: Person):
    return {"person": person.model_dump()}


client = TestClient(app)


def test_read_json():
    response = client.post("/person", json={"name": "John", "age": 20})
    assert response.status_code == 200
    assert response.json()['person']['name'] == "John"
    assert response.json()['person']['age'] == 20

def test_extra_json_param():
    response = client.post("/person", json={"name": "John", "age": 20, "comment": "extra param"})
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == "Extra inputs are not permitted"


def test_read_yaml():
    response = client.post("/person", content="name: Foo\nage: 30", headers={"Content-Type": "application/x-yaml"})
    assert response.status_code == 200
    assert response.json()['person']['name'] == "Foo"
    assert response.json()['person']['age'] == 30

def test_extra_yaml_param():
    response = client.post("/person", content="name: Foo\nage: 30\ncomment: extra param", headers={"Content-Type": "application/x-yaml"})
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == "Extra inputs are not permitted"