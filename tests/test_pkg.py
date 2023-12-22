from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from fastapi_yaml import YamlRoute

app = FastAPI()
app.router.route_class = YamlRoute


class Person(BaseModel, extra="forbid"):
    name: str
    age: int
    address: str = None


@app.post("/person")
def person(person: Person):
    return {"person": person.model_dump()}


client = TestClient(app)


def test_read_json():
    response = client.post("/person", json={"name": "John", "age": 20})
    assert response.status_code == 200
    assert response.json()["person"]["name"] == "John"
    assert response.json()["person"]["age"] == 20


def test_extra_json_param():
    response = client.post(
        "/person", json={"name": "John", "age": 20, "comment": "extra param"}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Extra inputs are not permitted"


def test_read_yaml():
    response = client.post(
        "/person",
        content="name: Foo\nage: 30",
        headers={"Content-Type": "application/x-yaml"},
    )
    assert response.status_code == 200
    assert response.json()["person"]["name"] == "Foo"
    assert response.json()["person"]["age"] == 30


def test_extra_yaml_param():
    response = client.post(
        "/person",
        content="name: Foo\nage: 30\ncomment: extra param",
        headers={"Content-Type": "application/x-yaml"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Extra inputs are not permitted"


def test_read_file_with_header_1():
    response = client.post(
        "/person",
        files=[
            ("upload_file", open("tests/files/person.yaml", "rb")),
            ("file_ext", open("tests/files/person_address.yaml", "rb")),
            ],
        headers={"handle-as-yaml": "enable"},
    )
    assert response.status_code == 200
    assert response.json()["person"]["name"] == "John Doe"
    assert response.json()["person"]["age"] == 30
    assert response.json()["person"]["address"] == "123 Main St"

def test_read_file_with_header_2():
    response = client.post(
        "/person",
        files=[
            ("upload_file", open("tests/files/person.yaml", "rb")),
            ("file_ext", open("tests/files/person_address.yaml", "rb")),
            ],
        headers={"HANDLE-AS-YAML": "True"},
    )
    assert response.status_code == 200
    assert response.json()["person"]["name"] == "John Doe"
    assert response.json()["person"]["age"] == 30
    assert response.json()["person"]["address"] == "123 Main St"

def test_read_file_errors():
    response = client.post(
        "/person",
        files=[
            ("upload_file", open("tests/files/person.yaml", "rb")),
            ("file_ext", open("tests/files/person_address.yaml", "rb")),
            ],
        headers={"handle-as-yaml": "false"},
    )
    assert response.status_code == 422


def test_read_file_using_boundaries():
    body = """
     ------WebKitFormBoundary7MA4YWxkTrZu0gW
    Content-Disposition: form-data; name="file"; filename="test.yaml"
    Content-Type: application/x-yaml

    name: Foo\nage: 30
    ------WebKitFormBoundary7MA4YWxkTrZu0gW--
    """
    response = client.post(
        "/person",
        data=body.strip(),
        headers={
            "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            # "handle-as-yaml": "enable",
        },
    )
    assert response.status_code == 200
