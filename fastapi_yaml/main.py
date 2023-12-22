from typing import Callable

import yaml
from fastapi import Request, Response
from fastapi.routing import APIRoute


def to_bool(s: str | bool | None) -> bool:
    if not s:
        return False
    if isinstance(s, bool):
        return s
    return s.lower().strip() in ["enable", "true", "yes", "1", "t", "y"]


class YamlRequest(Request):
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = await super().body()
            if self.headers.get("content-type") in [
                "application/x-yaml",
                "application/yaml",
                "text/yaml",
            ]:
                body = yaml.safe_load(body)
            elif self.headers.get("content-type").startswith(
                "multipart/form-data"
            ) and to_bool(self.headers.get("handle-as-yaml")):
                form = await self.form()
                contents = ""
                for file in form.values():
                    file_content = await file.read()
                    if isinstance(file_content, bytes):
                        file_content = file_content.decode()
                    contents += file_content + "\n"
                body = yaml.safe_load(contents)
            self._body = body
        return self._body


class YamlRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = YamlRequest(request.scope, request.receive)
            content_type = request.headers.get("content-type", "").strip()
            if content_type.startswith("multipart/form-data"):
                body_bytes = await request.body()
                if isinstance(body_bytes, bytes) and b"\r\n" not in body_bytes:
                    modified_body = body_bytes.replace(b"\n", b"\r\n")
                    original_receive = request.receive

                    async def custom_receive():
                        if modified_body:
                            return {
                                "type": "http.request",
                                "body": modified_body,
                                "more_body": False,
                            }
                        else:
                            return await original_receive()

                    request = Request(request.scope, custom_receive)
            return await original_route_handler(request)

        return custom_route_handler
