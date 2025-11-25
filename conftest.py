import random
import re
import requests
import pytest

BASE_URL = "https://qa-internship.avito.com"
API_PREFIX = "/api/1"

def gen_seller_id():
    r = (random.randint(111111, 999999))
    return int(r)

def take_uuid_from_status(status_text: str):
    if not status_text:
        return None
    else:
        uuid = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", status_text)
        return uuid.group(1)

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture
def seller_id():
    return gen_seller_id()

@pytest.fixture
def session():
    with requests.Session() as s:
        yield s

def create_item(session, base_url, payload, timeout=10):
    resp = session.post(base_url + API_PREFIX + "/item", json=payload, timeout=timeout)
    try:
        json = resp.json()
    except Exception:
        json = None
    return resp, json

def get_item_by_id(session, base_url, item_id, timeout=10):
    resp = session.get(f"{base_url}{API_PREFIX}/item/{item_id}", timeout=timeout)
    try:
        json = resp.json()
    except Exception:
        json = None
    return resp, json

def get_items_by_seller(session, base_url, seller_id, timeout=10):
    resp = session.get(f"{base_url}{API_PREFIX}/{seller_id}/item", timeout=timeout)
    try:
        json = resp.json()
    except Exception:
        json = None
    return resp, json

def get_statistic(session, base_url, item_id, timeout=10):
    resp = session.get(f"{base_url}{API_PREFIX}/statistic/{item_id}", timeout=timeout)
    try:
        json = resp.json()
    except Exception:
        json = None
    return resp, json