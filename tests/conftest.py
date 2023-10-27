import json

import pytest


@pytest.fixture
def mock_response_parse() -> dict:
    with open("tests/response/response_parse.json", "r") as file:
        data = json.load(file)
    return data


@pytest.fixture
def mock_response_classify() -> dict:
    with open("tests/response/response_classify.json", "r") as file:
        data = json.load(file)
    return data
