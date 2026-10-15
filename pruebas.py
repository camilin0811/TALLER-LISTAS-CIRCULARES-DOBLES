# -*- coding: utf-8 -*-
"""Banco de pruebas del taller: valida la lista circular doble y la API REST.

Ejecucion:   python pruebas.py
No levanta el servidor web: usa el cliente de pruebas que trae Flask.
"""
import os
import sys

# Permite ejecutar este archivo desde cualquier carpeta del disco.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dashboard_vehiculo as dv

# --- 1. prueba de la estructura pura -----------------------------------------
dv.demostracion_consola()

print("\n--- pruebas de borde ---")
L = dv.ListaCircularDoble()
assert L.esta_vacia() and len(L) == 0
assert L.avanzar_siguiente() is None and L.retroceder_anterior() is None
assert L.eliminar() is None
assert L.mostrar_actual() == "Sin modos cargados en la ECU"
assert str(L) == "(lista vacia)"

n = L.insertar(dv.ModoConduccion(nombre="Uno"))
assert L.cabeza is L.cola is L.actual is n
assert n.siguiente is n and n.anterior is n, "un solo nodo debe apuntarse a si mismo"
assert L.avanzar_siguiente().nombre == "Uno"
assert L.retroceder_anterior().nombre == "Uno"
print("1 nodo:", L, "| mostrar_actual:", L.mostrar_actual())

L.insertar(dv.ModoConduccion(nombre="Dos"))
L.insertar(dv.ModoConduccion(nombre="Tres"))
assert [m.nombre for m in L.obtener_todos()] == ["Uno", "Dos", "Tres"]
assert L.cola.siguiente is L.cabeza and L.cabeza.anterior is L.cola
print("3 nodos:", L)

# eliminar la cabeza estando sobre ella
L.seleccionar("Uno")
L.eliminar()
assert L.cabeza.dato.nombre == "Dos" and L.actual.dato.nombre == "Dos"
assert L.cola.siguiente is L.cabeza and L.cabeza.anterior is L.cola
print("tras borrar la cabeza:", L, "| cabeza:", L.cabeza.dato.nombre, "| cola:", L.cola.dato.nombre)

# eliminar la cola por nombre
L.eliminar("Tres")
assert L.cabeza is L.cola and len(L) == 1 and L.cabeza.siguiente is L.cabeza
print("tras borrar la cola:", L)

L.eliminar()
assert L.esta_vacia() and L.cabeza is None and L.cola is None and L.actual is None
print("tras borrar el ultimo:", L, "-> lista vacia OK")

# insercion despues del actual en medio
M = dv.ListaCircularDoble()
for nom in ("A", "B", "C"):
    M.insertar(dv.ModoConduccion(nombre=nom))
M.seleccionar("A")
M.insertar(dv.ModoConduccion(nombre="X"), despues_del_actual=True)
assert [m.nombre for m in M.obtener_todos()] == ["A", "X", "B", "C"]
M.seleccionar("C")
M.insertar(dv.ModoConduccion(nombre="Z"), despues_del_actual=True)
assert M.cola.dato.nombre == "Z", "insertar tras la cola debe mover la cola"
assert [m.nombre for m in M.obtener_todos()] == ["A", "X", "B", "C", "Z"]
print("inserciones intercaladas:", M)

# vuelta completa en los dos sentidos
nombres_ida = [M.avanzar_siguiente().nombre for _ in range(len(M))]
assert M.actual.dato.nombre == "C", "una vuelta completa debe volver al punto de partida"
nombres_vuelta = [M.retroceder_anterior().nombre for _ in range(len(M))]
assert M.actual.dato.nombre == "C"
print("vuelta horaria   :", nombres_ida)
print("vuelta antihoraria:", nombres_vuelta)

# --- 2. prueba de la API Flask -----------------------------------------------
print("\n--- pruebas de la API ---")
dv.ECU = dv.crear_lista_inicial()
c = dv.app.test_client()

r = c.get("/")
assert r.status_code == 200 and b"<!doctype html>" in r.data[:30].lower()
print("GET /            ->", r.status_code, "html de", len(r.data), "bytes")

e = c.get("/api/estado").get_json()
print("GET /api/estado  -> actual:", e["actual"]["nombre"], "| cabeza:", e["cabeza"], "| cola:", e["cola"])

e = c.post("/api/siguiente", json={}).get_json(); print("siguiente        ->", e["actual"]["nombre"])
e = c.post("/api/siguiente", json={}).get_json(); print("siguiente        ->", e["actual"]["nombre"])
e = c.post("/api/siguiente", json={}).get_json()
print("siguiente        ->", e["actual"]["nombre"], "(dio la vuelta: cola -> cabeza)")
e = c.post("/api/anterior", json={}).get_json()
print("anterior         ->", e["actual"]["nombre"], "(de la cabeza salto a la cola)")

e = c.post("/api/insertar", json={"nombre": "Drift", "icono": "D", "potencia": 98, "consumo": 95}).get_json()
assert e["cola"] == "Drift" and e["tamanio"] == 6
print("insertar Drift   -> tamanio", e["tamanio"], "| cola:", e["cola"])

r = c.post("/api/insertar", json={"nombre": "Drift"})
assert r.status_code == 400
print("duplicado        ->", r.status_code, r.get_json()["error"])

r = c.post("/api/insertar", json={"nombre": "   "})
assert r.status_code == 400
print("nombre vacio     ->", r.status_code, r.get_json()["error"])

e = c.post("/api/seleccionar", json={"nombre": "Sport"}).get_json()
assert e["actual"]["nombre"] == "Sport"
print("seleccionar Sport-> anterior:", e["anterior"], "| siguiente:", e["siguiente"])

e = c.post("/api/eliminar", json={}).get_json()
assert e["tamanio"] == 5 and all(n["nombre"] != "Sport" for n in e["nodos"])
print("eliminar actual  -> tamanio", e["tamanio"], "| actual:", e["actual"]["nombre"])

# vaciar por completo via API y comprobar que no explota
for _ in range(10):
    c.post("/api/eliminar", json={})
e = c.get("/api/estado").get_json()
assert e["vacia"] and e["tamanio"] == 0 and e["actual"] is None
print("vaciar todo      -> vacia:", e["vacia"], "| actual:", e["actual"])
r = c.post("/api/eliminar", json={}); assert r.status_code == 400
print("eliminar vacia   ->", r.status_code, r.get_json()["error"])
e = c.post("/api/insertar", json={"nombre": "Nuevo"}).get_json()
assert e["cabeza"] == "Nuevo" and e["cola"] == "Nuevo" and e["actual"]["nombre"] == "Nuevo"
print("insertar en vacia-> cabeza=cola=actual=", e["cabeza"])

e = c.post("/api/reiniciar", json={}).get_json()
assert e["tamanio"] == 5 and e["actual"]["nombre"] == "Confort"
print("reiniciar        -> tamanio", e["tamanio"], "| actual:", e["actual"]["nombre"])
print("bitacora[0]      :", e["bitacora"][0])

print("\nTODAS LAS PRUEBAS PASARON")
