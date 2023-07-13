# Overview

Handle YAML requests with FastAPI.

# Installation

```bash
pip install fastapi-yaml
```

# Usage

FastAPI Code:

```python
from fastapi import FastAPI
from fastapi_yaml import YamlRoute
from pydantic import BaseModel

app = FastAPI()
app.router.route_class = YamlRoute

class Person(BaseModel, extra='forbid'):
    name: str
    age: int

@app.post("/person")
def person(person: Person):
    return f"{person.name} is {person.age} years old"
```

HTTP Request:

```bash
curl --request POST \
  --url http://localhost:8000/person \
  --header "content-type: application/x-yaml" \
  --data "name: John Doe\nage: 42"
```

# Tests

```bash
poetry run pytest --cov fastapi_yaml tests/
```

## Coverage

```text
---------- coverage: platform darwin, python 3.11.2-final-0 ----------
Name                       Stmts   Miss  Cover
----------------------------------------------
fastapi_yaml/__init__.py       1      0   100%
fastapi_yaml/main.py          20      0   100%
----------------------------------------------
TOTAL                         21      0   100%
```
