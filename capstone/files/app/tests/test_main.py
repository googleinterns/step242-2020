# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import builtins
import tempfile
from os import path

import main
import pytest
from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_homepage():
    response = client.get('/')
    assert response.status_code == 200
    assert response.template.name == "form.html.jinja"
    assert "request" in response.context


def test_download_file_ok(monkeypatch):
    f = tempfile.NamedTemporaryFile()
    content = b"This is an example \x00\xff"
    f.write(content)
    f.seek(0)

    def join(a, b):
        return f.name

    monkeypatch.setattr(path, "join", join)

    response = client.get('/1111')

    assert response.content == content
    f.close()


@pytest.mark.parametrize("file_name", [
    "some-file", "../main.py"
])
def test_download_file_bad(file_name):
    response = client.get(file_name)
    assert response.status_code == 400


def test_upload_file(monkeypatch):
    def open(path, type):
        return tempfile.TemporaryFile()

    monkeypatch.setattr(builtins, "open", open)

    response = client.post("/upload-file/",
                           files={
                               "file": ("This is an example \x00\xff", "filename.txt")
                           })

    assert response.status_code == 200
    assert response.template.name == "file_name.html.jinja"
    assert "request" in response.context
    assert "name" in response.context
