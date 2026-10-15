# -*- coding: utf-8 -*-
"""Test bench for the workshop: validates the circular doubly linked list and the REST API.

Run it with:   python tests.py
It never starts the web server: it uses the test client shipped with Flask.
"""
import os
import sys

# Allows running this file from any folder on disk.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vehicle_dashboard as vd

# --- 1. testing the bare data structure --------------------------------------
vd.console_demo()

print("\n--- edge cases ---")
first = vd.CircularDoublyLinkedList()
assert first.is_empty() and len(first) == 0
assert first.move_next() is None and first.move_previous() is None
assert first.remove() is None
assert first.show_current() == "Sin modos cargados en la ECU"
assert str(first) == "(lista vacia)"

only = first.insert(vd.DrivingMode(name="Uno"))
assert first.head is first.tail is first.current is only
assert only.next is only and only.prev is only, "a single node must point to itself"
assert first.move_next().name == "Uno"
assert first.move_previous().name == "Uno"
print("1 node :", first, "| show_current:", first.show_current())

first.insert(vd.DrivingMode(name="Dos"))
first.insert(vd.DrivingMode(name="Tres"))
assert [mode.name for mode in first.get_all()] == ["Uno", "Dos", "Tres"]
assert first.tail.next is first.head and first.head.prev is first.tail
print("3 nodes:", first)

# removing the head while standing on it
first.select("Uno")
first.remove()
assert first.head.data.name == "Dos" and first.current.data.name == "Dos"
assert first.tail.next is first.head and first.head.prev is first.tail
print("after removing the head:", first, "| head:", first.head.data.name,
      "| tail:", first.tail.data.name)

# removing the tail by name
first.remove("Tres")
assert first.head is first.tail and len(first) == 1 and first.head.next is first.head
print("after removing the tail:", first)

first.remove()
assert first.is_empty() and first.head is None and first.tail is None and first.current is None
print("after removing the last one:", first, "-> empty list OK")

# splicing in the middle with after_current
second = vd.CircularDoublyLinkedList()
for name in ("A", "B", "C"):
    second.insert(vd.DrivingMode(name=name))
second.select("A")
second.insert(vd.DrivingMode(name="X"), after_current=True)
assert [mode.name for mode in second.get_all()] == ["A", "X", "B", "C"]
second.select("C")
second.insert(vd.DrivingMode(name="Z"), after_current=True)
assert second.tail.data.name == "Z", "inserting behind the tail must move the tail"
assert [mode.name for mode in second.get_all()] == ["A", "X", "B", "C", "Z"]
print("spliced insertions:", second)

# a full lap in both directions
forward = [second.move_next().name for _ in range(len(second))]
assert second.current.data.name == "C", "a full lap must land back on the starting node"
backward = [second.move_previous().name for _ in range(len(second))]
assert second.current.data.name == "C"
print("clockwise lap        :", forward)
print("counter-clockwise lap:", backward)

# --- 2. testing the Flask API ------------------------------------------------
print("\n--- API tests ---")
vd.ECU = vd.create_initial_list()
client = vd.app.test_client()

reply = client.get("/")
assert reply.status_code == 200 and b"<!doctype html>" in reply.data[:30].lower()
print("GET /            ->", reply.status_code, "html of", len(reply.data), "bytes")

state = client.get("/api/state").get_json()
print("GET /api/state   -> current:", state["current"]["name"],
      "| head:", state["head"], "| tail:", state["tail"])

state = client.post("/api/next", json={}).get_json(); print("next             ->", state["current"]["name"])
state = client.post("/api/next", json={}).get_json(); print("next             ->", state["current"]["name"])
state = client.post("/api/next", json={}).get_json()
print("next             ->", state["current"]["name"], "(wrapped around: tail -> head)")
state = client.post("/api/previous", json={}).get_json()
print("previous         ->", state["current"]["name"], "(from the head it jumped to the tail)")

state = client.post("/api/insert",
                    json={"name": "Drift", "icon": "D", "power": 98, "consumption": 95}).get_json()
assert state["tail"] == "Drift" and state["size"] == 6
print("insert Drift     -> size", state["size"], "| tail:", state["tail"])

reply = client.post("/api/insert", json={"name": "Drift"})
assert reply.status_code == 400
print("duplicate name   ->", reply.status_code, reply.get_json()["error"])

reply = client.post("/api/insert", json={"name": "   "})
assert reply.status_code == 400
print("blank name       ->", reply.status_code, reply.get_json()["error"])

state = client.post("/api/select", json={"name": "Sport"}).get_json()
assert state["current"]["name"] == "Sport"
print("select Sport     -> prev:", state["prev"], "| next:", state["next"])

state = client.post("/api/remove", json={}).get_json()
assert state["size"] == 5 and all(node["name"] != "Sport" for node in state["nodes"])
print("remove current   -> size", state["size"], "| current:", state["current"]["name"])

# empty the list through the API and make sure nothing blows up
for _ in range(10):
    client.post("/api/remove", json={})
state = client.get("/api/state").get_json()
assert state["empty"] and state["size"] == 0 and state["current"] is None
print("remove everything-> empty:", state["empty"], "| current:", state["current"])
reply = client.post("/api/remove", json={}); assert reply.status_code == 400
print("remove on empty  ->", reply.status_code, reply.get_json()["error"])
state = client.post("/api/insert", json={"name": "Nuevo"}).get_json()
assert state["head"] == "Nuevo" and state["tail"] == "Nuevo" and state["current"]["name"] == "Nuevo"
print("insert on empty  -> head = tail = current =", state["head"])

state = client.post("/api/reset", json={}).get_json()
assert state["size"] == 5 and state["current"]["name"] == "Confort"
print("reset            -> size", state["size"], "| current:", state["current"]["name"])
print("log[0]           :", state["log"][0])

print("\nEVERY TEST PASSED")
