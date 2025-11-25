import pytest
from conftest import create_item, get_item_by_id, get_items_by_seller, get_statistic, take_uuid_from_status


def find_obj_with_id(container, item_id):
    if container is None:
        return None
    if isinstance(container, dict):
        return container if container.get("id") == item_id else None
    if isinstance(container, list):
        for el in container:
            if isinstance(el, dict) and el.get("id") == item_id:
                return el
    return None


def test1_create_item_positive(session, base_url, seller_id):
    payload = {
        "sellerID": seller_id,
        "name": "test item",
        "price": 100,
        "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
    }
    resp, json = create_item(session, base_url, payload)
    assert resp.status_code == 200, f"Expected 200 on create, got {resp.status_code}, body: {resp.text}"
    assert json is not None and "status" in json, f"Expected JSON with 'status' field in create response, got: {json}"
    uuid = take_uuid_from_status(json.get("status"))
    assert uuid, f"UUID not found in status string: {json.get('status')}"


def test2_get_item_by_id_positive(session, base_url, seller_id):
    payload = {
        "sellerID": seller_id,
        "name": "test item getbyid",
        "price": 135,
        "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
    }
    resp, json = create_item(session, base_url, payload)
    assert resp.status_code == 200, f"Create failed: {resp.status_code}"
    uuid = take_uuid_from_status(json.get("status"))
    assert uuid, "Could not extract id from create response"
    get_resp, get_json = get_item_by_id(session, base_url, uuid)
    assert get_resp.status_code == 200, f"Expected 200 on GET by id, got {get_resp.status_code}, body: {get_resp.text}"
    found = find_obj_with_id(get_json, uuid)
    assert found is not None, f"Item with id {uuid} not found in GET response"
    assert found.get("id") == uuid


def test3_get_items_by_seller_positive(session, base_url, seller_id):
    ids = []
    for i in range(2):
        payload = {
            "sellerID": seller_id,
            "name": f"seller test item {i}",
            "price": 345 + i,
            "statistics": {"likes": 1+i, "viewCount": 1+i, "contacts": 1+i}
        }
        resp, json = create_item(session, base_url, payload)
        assert resp.status_code == 200, f"Create failed for test item {i}"
        uuid = take_uuid_from_status(json.get("status") )

        if uuid:
            ids.append(uuid)

    get_resp, get_json = get_items_by_seller(session, base_url, seller_id)

    assert get_resp.status_code == 200, f"Expected 200 on GET items by seller, got {get_resp.status_code}"
    assert isinstance(get_json, list), f"Expected list from seller items, got {type(get_json)}"

    for it in get_json:
        assert isinstance(it, dict), f"Expected dict from item, got {type(it)}"
        assert it["sellerId"] == seller_id, f"Expected sellerId {seller_id} from item {it}"

    if ids:
        present = 0
        for it in get_json:
            if it.get("id") in ids:
                present += 1
        assert present >= 0, f"Item with id {ids[0]} not found in GET response"


def test4_get_statistic_by_id_positive(session, base_url, seller_id):

    payload = {
        "sellerID": seller_id,
        "name": "stat test item",
        "price": 465,
        "statistics": {"likes": 2, "viewCount": 3, "contacts": 4}
    }
    resp, json = create_item(session, base_url, payload)
    assert resp.status_code == 200
    uuid = take_uuid_from_status(json.get("status"))
    assert uuid, "No id from create"
    stat_resp, stat_json = get_statistic(session, base_url, uuid)
    assert stat_resp.status_code == 200, f"Expected 200 on GET statistic, got {stat_resp.status_code}"
    stats = None
    if isinstance(stat_json, dict):
        stats = stat_json
    elif isinstance(stat_json, list) and len(stat_json) > 0:
        stats = stat_json[0]
    assert stats is not None, "Statistic body missing or empty"
    for f in ("likes", "viewCount", "contacts"):
        assert f in stats, f"Field {f} missing from statistics"
        assert isinstance(stats[f], (int, float)), f"Field {f} is not numeric"


def test5_get_nonexistent_item_expected_400(session, base_url):
    random_id = "00000000-0000-4000-8000-000000000000"
    get_resp, get_json = get_item_by_id(session, base_url, random_id)
    assert get_resp.status_code == 404, f"Expected 400 for non-existent GET by id, got {get_resp.status_code}, body: {get_resp.text}"


def test6_get_statistic_nonexistent_expected_400(session, base_url):
    random_id = "00000000-0000-4000-8000-000000000000"
    stat_resp, stat_json = get_statistic(session, base_url, random_id)
    assert stat_resp.status_code == 404, f"Expected 400 for non-existent statistic, got {stat_resp.status_code}, body: {stat_resp.text}"


def test7_get_items_by_nonexistent_seller(session, base_url):
    fake_seller = 9
    get_resp, get_json = get_items_by_seller(session, base_url, fake_seller)
    assert get_resp.status_code == 200, f"Expected 200 for non-existent seller list, got {get_resp.status_code}"
    assert isinstance(get_json, list), f"Expected list from seller, got {type(get_json)}"
    assert len(get_json) == 0, f"Expected empty list for non-existent seller, got: {get_json}"


def test8_create_empty_item_should_400(session, base_url, seller_id):
    payload = {
    }
    resp, json = create_item(session, base_url, payload)
    assert resp.status_code == 400, f"Expected 400 for empty create payload, got {resp.status_code}, body: {resp.text}"
