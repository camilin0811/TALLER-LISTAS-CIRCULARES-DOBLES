# -*- coding: utf-8 -*-
"""
===============================================================================
 TALLER: LISTAS CIRCULARES DOBLEMENTE ENLAZADAS
 Caso de estudio: Sistema de Infotenimiento y Modos de Conduccion
                  de un Vehiculo Inteligente
===============================================================================

 ESTRUCTURA DEL ARCHIVO
 ----------------------
   BLOQUE 1 : ModoConduccion .......... el "dato" que viaja dentro de cada nodo
   BLOQUE 2 : Nodo .................... la celda con punteros anterior/siguiente
   BLOQUE 3 : ListaCircularDoble ...... la estructura de datos hecha a mano
   BLOQUE 4 : datos iniciales ......... los 5 modos de fabrica del vehiculo
   BLOQUE 5 : Backend Flask ........... API REST que expone la lista
   BLOQUE 6 : Frontend HTML/CSS/JS .... el tablero digital del automovil
   BLOQUE 7 : Arranque ................ demo por consola + servidor web


 POR QUE UNA LISTA CIRCULAR DOBLEMENTE ENLAZADA EN LA INDUSTRIA AUTOMOTRIZ
 ------------------------------------------------------------------------
 El conductor solo tiene DOS estimulos fisicos disponibles: un boton/leva que
 dice "siguiente" y otro que dice "anterior" (o un dial que gira en los dos
 sentidos). No puede escribir un indice ni elegir una posicion: solo avanza o
 retrocede. Esa interfaz exige exactamente tres propiedades:

   1) CIRCULAR -> El conductor nunca debe encontrar un "fin de lista". Si esta
      en Individual (el ultimo modo) y vuelve a pulsar la leva derecha, debe
      aparecer Eco otra vez. En una lista normal habria que preguntar en cada
      pulsacion "¿ya llegue al final? entonces reinicio al principio". Aqui el
      ultimo nodo apunta al primero, asi que ese caso especial DESAPARECE: el
      recorrido es infinito sin un solo 'if'.

   2) DOBLEMENTE ENLAZADA -> La leva izquierda tiene que retroceder un modo.
      Con punteros solo hacia adelante habria que recorrer toda la lista para
      encontrar al vecino de atras: O(n) y, en un volante, un retardo visible.
      Con el puntero 'anterior' retroceder cuesta O(1), igual que avanzar.
      Simetria de costo = simetria de la experiencia del conductor.

   3) INSERCION / ELIMINACION BARATA -> Un usuario agrega el perfil
      "Individual 2", el taller desactiva Off-Road en un auto sin traccion
      total, o una emisora de radio se guarda o se borra. En una lista enlazada
      eso es reconectar cuatro punteros, O(1), sin desplazar el resto de los
      elementos como ocurriria en un arreglo.

 Con lo anterior, cada pulsacion del volante se resuelve en TIEMPO CONSTANTE y
 con una sola instruccion: self.actual = self.actual.siguiente (o .anterior).
 Ese es el corazon del taller.
"""

from dataclasses import dataclass, asdict


# ==============================================================================
# BLOQUE 1 - EL DATO: un modo de conduccion del vehiculo
# ==============================================================================
@dataclass
class ModoConduccion:
    """Informacion que la computadora del auto aplica al elegir un modo.

    Es solo el CONTENIDO (la carga util). No sabe nada de punteros ni de listas:
    esa es la responsabilidad del Nodo. Separar dato y nodo es el principio de
    responsabilidad unica de la POO: si manana el dato cambia a 'EmisoraRadio',
    la lista circular sigue funcionando sin tocar una linea.
    """
    nombre: str                      # texto que se muestra en el tablero
    icono: str = "*"                 # emoji/caracter que identifica el modo
    color: str = "#39d98a"           # color de acento del tablero (hex)
    descripcion: str = ""            # frase corta explicativa
    potencia: int = 50               # 0-100, respuesta del acelerador
    consumo: int = 50                # 0-100, consumo estimado de combustible
    direccion: str = "Normal"        # asistencia de la direccion
    suspension: str = "Normal"       # dureza de la suspension
    traccion: str = "Delantera"      # reparto de par a las ruedas

    def como_diccionario(self) -> dict:
        """Convierte el dato a dict para poder enviarlo como JSON al navegador."""
        return asdict(self)


# ==============================================================================
# BLOQUE 2 - EL NODO: dato + dos punteros
# ==============================================================================
class Nodo:
    """Una celda de la lista.

    Contiene el dato y DOS referencias:
        siguiente -> la celda que esta a la derecha
        anterior  -> la celda que esta a la izquierda

    En una lista circular NUNCA quedan en None despues de insertar: si la lista
    tiene un solo nodo, ese nodo se apunta a si mismo en las dos direcciones.
    """

    def __init__(self, dato: ModoConduccion):
        self.dato = dato          # la carga util (un ModoConduccion)
        self.siguiente = None     # se conecta al insertar en la lista
        self.anterior = None      # se conecta al insertar en la lista

    def __repr__(self) -> str:
        # Representacion util para depurar por consola.
        ant = self.anterior.dato.nombre if self.anterior else "None"
        sig = self.siguiente.dato.nombre if self.siguiente else "None"
        return f"[{ant}] <- ({self.dato.nombre}) -> [{sig}]"


# ==============================================================================
# BLOQUE 3 - LA ESTRUCTURA DE DATOS, CONSTRUIDA DESDE CERO
# ==============================================================================
class ListaCircularDoble:
    """Lista circular doblemente enlazada implementada manualmente.

    No se usa ninguna lista nativa de Python como estructura principal: todo el
    almacenamiento vive en los objetos Nodo y en sus punteros. Las unicas listas
    de Python que aparecen son de SALIDA (obtener_todos / estado), es decir
    fotografias temporales para dibujar la interfaz.

    Atributos de control:
        cabeza  -> primer nodo de la lista   (equivale al modo Eco)
        cola    -> ultimo nodo de la lista   (equivale al modo Individual)
        actual  -> nodo seleccionado ahora mismo por el conductor
        tamanio -> cantidad de nodos, para no tener que contarlos cada vez
    """

    # ---------------------------------------------------------------- creacion
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.actual = None
        self.tamanio = 0

    # --------------------------------------------------------------- consultas
    def esta_vacia(self) -> bool:
        """True si no hay ningun nodo. Primera pregunta de casi todos los metodos."""
        return self.cabeza is None

    def __len__(self) -> int:
        """Permite escribir len(lista). Devuelve el contador interno: O(1)."""
        return self.tamanio

    def buscar(self, nombre: str):
        """Devuelve el Nodo cuyo dato se llama nombre, o None si no existe.

        Recorre la lista UNA sola vuelta. El corte del bucle no es "nodo is None"
        como en una lista normal, sino "volvi a la cabeza": asi se evita el bucle
        infinito que provoca la circularidad.
        """
        if self.esta_vacia():
            return None
        nodo = self.cabeza
        while True:
            if nodo.dato.nombre.lower() == nombre.strip().lower():
                return nodo
            nodo = nodo.siguiente
            if nodo is self.cabeza:      # dimos la vuelta completa
                return None

    # --------------------------------------------------------------- insertar
    def insertar(self, dato: ModoConduccion, despues_del_actual: bool = False):
        """Agrega un nuevo modo a la lista y devuelve el Nodo creado.

        despues_del_actual = False -> lo agrega al final (detras de la cola).
        despues_del_actual = True  -> lo intercala justo despues del modo actual,
                                      que es lo natural cuando el conductor
                                      personaliza un perfil aqui mismo.

        Coste O(1): no se recorre nada, solo se reconectan punteros.
        """
        nuevo = Nodo(dato)

        # CASO A: la lista estaba vacia. El nodo es cabeza, cola y actual a la
        # vez, y se cierra el circulo apuntandose a si mismo en ambos sentidos.
        if self.esta_vacia():
            nuevo.siguiente = nuevo
            nuevo.anterior = nuevo
            self.cabeza = nuevo
            self.cola = nuevo
            self.actual = nuevo
            self.tamanio += 1
            return nuevo

        # CASO B: insertar justo despues del nodo actual.
        if despues_del_actual:
            izquierda = self.actual              # vecino de la izquierda
            derecha = self.actual.siguiente      # vecino de la derecha
            nuevo.anterior = izquierda           # 1. el nuevo mira a la izquierda
            nuevo.siguiente = derecha            # 2. el nuevo mira a la derecha
            izquierda.siguiente = nuevo          # 3. la izquierda lo adopta
            derecha.anterior = nuevo             # 4. la derecha lo adopta
            if izquierda is self.cola:           # si se inserto tras la cola,
                self.cola = nuevo                # el nuevo pasa a ser la cola
            self.tamanio += 1
            return nuevo

        # CASO C: insertar al final (entre la cola vieja y la cabeza).
        nuevo.anterior = self.cola               # 1. detras del nuevo va la cola
        nuevo.siguiente = self.cabeza            # 2. delante del nuevo, la cabeza
        self.cola.siguiente = nuevo              # 3. la cola ahora apunta al nuevo
        self.cabeza.anterior = nuevo             # 4. la cabeza retrocede al nuevo
        self.cola = nuevo                        # 5. el nuevo es la nueva cola
        self.tamanio += 1
        return nuevo

    # --------------------------------------------------------------- eliminar
    def eliminar(self, nombre: str = None):
        """Quita un nodo y devuelve su dato (o None si no habia nada que quitar).

        Sin argumento elimina el modo ACTUAL, que es el gesto real del tablero:
        borrar el que estoy viendo. Con nombre, elimina ese en concreto.
        """
        if self.esta_vacia():
            return None

        objetivo = self.actual if nombre is None else self.buscar(nombre)
        if objetivo is None:
            return None

        dato = objetivo.dato

        # CASO A: era el unico nodo -> la lista queda completamente vacia.
        if self.tamanio == 1:
            self.cabeza = None
            self.cola = None
            self.actual = None
            self.tamanio = 0
            return dato

        # CASO B: hay mas nodos -> se cose el hueco uniendo sus dos vecinos.
        izquierda = objetivo.anterior
        derecha = objetivo.siguiente
        izquierda.siguiente = derecha          # el de la izquierda salta el hueco
        derecha.anterior = izquierda           # el de la derecha tambien

        # Si el eliminado era un extremo, el extremo se desplaza a su vecino.
        if objetivo is self.cabeza:
            self.cabeza = derecha
        if objetivo is self.cola:
            self.cola = izquierda
        # Si el conductor estaba viendo el modo borrado, el tablero pasa al
        # siguiente: nunca se queda sin un modo activo.
        if objetivo is self.actual:
            self.actual = derecha

        # Se aisla el nodo retirado para que el recolector de basura lo libere.
        objetivo.siguiente = None
        objetivo.anterior = None
        self.tamanio -= 1
        return dato

    # ------------------------------------------------- navegacion del volante
    def avanzar_siguiente(self):
        """Leva derecha del volante: pasa al modo siguiente. O(1).

        Aqui se ve el beneficio de la circularidad: no hay que comprobar si se
        llego al final, porque cola.siguiente YA es la cabeza.
        """
        if self.esta_vacia():
            return None
        self.actual = self.actual.siguiente
        return self.actual.dato

    def retroceder_anterior(self):
        """Leva izquierda del volante: vuelve al modo previo. O(1).

        Gracias al puntero anterior, retroceder cuesta lo mismo que avanzar; y
        como cabeza.anterior es la cola, desde Eco se salta directo a Individual.
        """
        if self.esta_vacia():
            return None
        self.actual = self.actual.anterior
        return self.actual.dato

    def seleccionar(self, nombre: str):
        """Salto directo a un modo (el conductor toca su icono en la pantalla)."""
        nodo = self.buscar(nombre)
        if nodo is None:
            return None
        self.actual = nodo
        return nodo.dato

    # ----------------------------------------------------------------- lectura
    def mostrar_actual(self) -> str:
        """Texto del modo activo, tal como lo pintaria el tablero.

        Muestra tambien a sus dos vecinos para dejar visible el enlace doble.
        """
        if self.esta_vacia():
            return "Sin modos cargados en la ECU"
        anterior = self.actual.anterior.dato.nombre
        actual = self.actual.dato.nombre
        siguiente = self.actual.siguiente.dato.nombre
        return f"<< {anterior}  |  [ {actual} ]  |  {siguiente} >>"

    def obtener_todos(self) -> list:
        """Lista de Python con todos los datos, en orden desde la cabeza.

        IMPORTANTE: esta lista es solo una copia de salida para dibujar la
        interfaz; el almacenamiento real sigue siendo la cadena de nodos.
        """
        elementos = []
        if self.esta_vacia():
            return elementos
        nodo = self.cabeza
        while True:
            elementos.append(nodo.dato)
            nodo = nodo.siguiente
            if nodo is self.cabeza:     # condicion de parada circular
                break
        return elementos

    def __iter__(self):
        """Permite recorrer la lista con un for, dando una sola vuelta."""
        return iter(self.obtener_todos())

    def __str__(self) -> str:
        """Dibujo de la lista en una linea, con el actual entre corchetes."""
        if self.esta_vacia():
            return "(lista vacia)"
        piezas = []
        for modo in self.obtener_todos():
            if self.actual and modo.nombre == self.actual.dato.nombre:
                piezas.append(f"[{modo.nombre}]")
            else:
                piezas.append(modo.nombre)
        return "... <-> " + " <-> ".join(piezas) + " <-> ..."

    # ------------------------------------------- fotografia para el frontend
    def estado(self) -> dict:
        """Empaqueta TODO lo que el tablero necesita saber, en formato JSON.

        Por cada nodo se envian los nombres de sus vecinos: asi el navegador
        dibuja las flechas reales de los punteros en lugar de suponerlas.
        """
        nodos = []
        if not self.esta_vacia():
            nodo = self.cabeza
            while True:
                datos = nodo.dato.como_diccionario()
                datos["anterior"] = nodo.anterior.dato.nombre
                datos["siguiente"] = nodo.siguiente.dato.nombre
                datos["es_cabeza"] = nodo is self.cabeza
                datos["es_cola"] = nodo is self.cola
                datos["es_actual"] = nodo is self.actual
                nodos.append(datos)
                nodo = nodo.siguiente
                if nodo is self.cabeza:
                    break

        return {
            "vacia": self.esta_vacia(),
            "tamanio": self.tamanio,
            "cabeza": self.cabeza.dato.nombre if self.cabeza else None,
            "cola": self.cola.dato.nombre if self.cola else None,
            "actual": self.actual.dato.como_diccionario() if self.actual else None,
            "anterior": self.actual.anterior.dato.nombre if self.actual else None,
            "siguiente": self.actual.siguiente.dato.nombre if self.actual else None,
            "nodos": nodos,
            "texto": self.mostrar_actual(),
            "dibujo": str(self),
        }


# ==============================================================================
# BLOQUE 4 - DATOS DE FABRICA: los 5 modos que trae el vehiculo
# ==============================================================================
MODOS_DE_FABRICA = [
    ModoConduccion(
        nombre="Eco",
        icono="🌿",
        color="#39d98a",
        descripcion="Maxima autonomia. Suaviza el acelerador y corta el par innecesario.",
        potencia=35, consumo=22,
        direccion="Ligera", suspension="Blanda", traccion="Delantera",
    ),
    ModoConduccion(
        nombre="Confort",
        icono="🛋️",
        color="#4aa8ff",
        descripcion="Ajuste equilibrado para ciudad y carretera. Es el modo por defecto.",
        potencia=55, consumo=45,
        direccion="Asistida", suspension="Adaptativa", traccion="Delantera",
    ),
    ModoConduccion(
        nombre="Sport",
        icono="🏁",
        color="#ff4d5a",
        descripcion="Respuesta inmediata, cambios tardios y escape activo.",
        potencia=92, consumo=85,
        direccion="Firme", suspension="Rigida", traccion="Trasera 70/30",
    ),
    ModoConduccion(
        nombre="Off-Road",
        icono="⛰️",
        color="#f0a63c",
        descripcion="Control de descenso, bloqueo de diferencial y altura elevada.",
        potencia=70, consumo=78,
        direccion="Pesada", suspension="Elevada", traccion="Integral 50/50",
    ),
    ModoConduccion(
        nombre="Individual",
        icono="🎛️",
        color="#b07cff",
        descripcion="Perfil libre del conductor. Guarda su combinacion favorita.",
        potencia=65, consumo=60,
        direccion="Personalizada", suspension="Personalizada", traccion="Configurable",
    ),
]


def crear_lista_inicial() -> ListaCircularDoble:
    """Construye la lista circular doble con los modos de fabrica.

    Inserta uno por uno al final; al terminar, Individual.siguiente == Eco y
    Eco.anterior == Individual, o sea el circulo ya quedo cerrado.
    """
    lista = ListaCircularDoble()
    for modo in MODOS_DE_FABRICA:
        # Se inserta una COPIA del dato para que reiniciar no arrastre cambios.
        lista.insertar(ModoConduccion(**modo.como_diccionario()))
    lista.seleccionar("Confort")   # el auto arranca en Confort, como los reales
    return lista


# ==============================================================================
# BLOQUE 5 - BACKEND: servidor Flask que expone la lista como API REST
# ==============================================================================
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# Unica instancia de la estructura: representa la memoria de la ECU del auto.
ECU = crear_lista_inicial()

# Bitacora de punteros. Se mantiene FUERA de la clase para que la estructura de
# datos quede pura (responsabilidad unica): la lista enlaza nodos, la aplicacion
# registra lo que el conductor hizo.
BITACORA = []


def anotar(mensaje: str) -> None:
    """Guarda una linea en la bitacora, conservando solo las 12 mas recientes."""
    BITACORA.insert(0, mensaje)
    del BITACORA[12:]


def respuesta():
    """Devuelve el estado completo de la lista + la bitacora, en JSON."""
    datos = ECU.estado()
    datos["bitacora"] = list(BITACORA)
    return jsonify(datos)


@app.get("/api/estado")
def api_estado():
    """Fotografia actual. El navegador la pide al cargar la pagina."""
    return respuesta()


@app.post("/api/siguiente")
def api_siguiente():
    """Leva derecha: actual = actual.siguiente."""
    previo = ECU.actual.dato.nombre if ECU.actual else "-"
    modo = ECU.avanzar_siguiente()
    if modo:
        anotar(f"▶  {previo}.siguiente  ->  {modo.nombre}")
    return respuesta()


@app.post("/api/anterior")
def api_anterior():
    """Leva izquierda: actual = actual.anterior."""
    previo = ECU.actual.dato.nombre if ECU.actual else "-"
    modo = ECU.retroceder_anterior()
    if modo:
        anotar(f"◀  {previo}.anterior  ->  {modo.nombre}")
    return respuesta()


@app.post("/api/seleccionar")
def api_seleccionar():
    """Salto directo tocando un nodo del anillo."""
    nombre = (request.json or {}).get("nombre", "")
    modo = ECU.seleccionar(nombre)
    if modo:
        anotar(f"⦿  salto directo  ->  {modo.nombre}")
    return respuesta()


@app.post("/api/insertar")
def api_insertar():
    """Crea un modo nuevo y lo enlaza en la lista.

    El formulario del tablero manda nombre, icono, color, descripcion, potencia,
    consumo y donde insertarlo (al final o despues del actual).
    """
    cuerpo = request.json or {}
    nombre = str(cuerpo.get("nombre", "")).strip()
    if not nombre:
        return jsonify({"error": "El nombre del modo no puede estar vacio"}), 400
    if ECU.buscar(nombre):
        return jsonify({"error": f"El modo '{nombre}' ya existe en la lista"}), 400

    nuevo = ModoConduccion(
        nombre=nombre,
        icono=str(cuerpo.get("icono") or "🎚️")[:4],
        color=str(cuerpo.get("color") or "#00e0d0"),
        descripcion=str(cuerpo.get("descripcion") or "Modo definido por el conductor."),
        potencia=max(0, min(100, int(cuerpo.get("potencia", 50)))),
        consumo=max(0, min(100, int(cuerpo.get("consumo", 50)))),
        direccion="Personalizada",
        suspension="Personalizada",
        traccion="Configurable",
    )
    despues = bool(cuerpo.get("despues_del_actual", False))
    ECU.insertar(nuevo, despues_del_actual=despues)
    destino = "despues del actual" if despues else "al final (nueva cola)"
    anotar(f"+  insertado '{nombre}' {destino} | 4 punteros reconectados")
    return respuesta()


@app.post("/api/eliminar")
def api_eliminar():
    """Elimina el modo actual (o uno por nombre) y cose el hueco."""
    nombre = (request.json or {}).get("nombre") or None
    if ECU.esta_vacia():
        return jsonify({"error": "La lista ya esta vacia"}), 400
    dato = ECU.eliminar(nombre)
    if dato is None:
        return jsonify({"error": "No se encontro ese modo"}), 400
    anotar(f"-  eliminado '{dato.nombre}' | sus vecinos quedaron unidos")
    return respuesta()


@app.post("/api/reiniciar")
def api_reiniciar():
    """Restaura los 5 modos de fabrica (boton RESET de la ECU)."""
    global ECU
    ECU = crear_lista_inicial()
    BITACORA.clear()
    anotar("⟲  ECU reiniciada con los 5 modos de fabrica")
    return respuesta()


@app.get("/")
def inicio():
    """Entrega el tablero. Se manda como texto plano HTML, sin plantillas Jinja,
    porque todos los datos llegan despues por fetch a /api/*."""
    return Response(TABLERO_HTML, mimetype="text/html")


# ==============================================================================
# BLOQUE 6 - FRONTEND: el tablero digital del automovil (HTML + CSS + JS)
# ==============================================================================
# Va dentro de una cadena de texto para que todo el taller quepa en un unico
# archivo .py. El navegador recibe esta cadena tal cual y despues conversa con
# el backend por fetch() contra las rutas /api/*.
TABLERO_HTML = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sistema de Infotenimiento y Modos de Conducción de un Vehículo Inteligente</title>
<style>
  :root{
    --acento:#4aa8ff;
    --fondo:#070a10;
    --panel:#101722;
    --panel2:#161f2e;
    --borde:#223044;
    --texto:#e7eef8;
    --suave:#8ba0bd;
    --oro:#ffc34d;
  }
  *{box-sizing:border-box}
  body{
    margin:0; padding:24px 18px 48px;
    background:
      radial-gradient(900px 500px at 50% -10%, rgba(74,168,255,.10), transparent 60%),
      var(--fondo);
    color:var(--texto);
    font-family:"Segoe UI",system-ui,-apple-system,Roboto,sans-serif;
    min-height:100vh;
  }
  .marco{max-width:1180px;margin:0 auto}

  /* ------------------------------------------------ encabezado del vehiculo */
  header{display:flex;flex-wrap:wrap;align-items:center;gap:14px;
         border-bottom:1px solid var(--borde);padding-bottom:14px;margin-bottom:22px}
  header .logo{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;
         background:linear-gradient(145deg,var(--acento),rgba(0,0,0,.4));font-size:22px}
  header h1{font-size:17px;margin:0;letter-spacing:.2px;font-weight:600}
  header p{margin:2px 0 0;font-size:12px;color:var(--suave)}
  .chip{margin-left:auto;font-size:11px;letter-spacing:1.5px;color:var(--suave);
        border:1px solid var(--borde);border-radius:999px;padding:6px 12px;text-transform:uppercase}

  /* -------------------------------------------------------------- cuadricula */
  .rejilla{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:18px}
  @media (max-width:900px){.rejilla{grid-template-columns:1fr}}
  .caja{background:linear-gradient(180deg,var(--panel),var(--panel2));
        border:1px solid var(--borde);border-radius:18px;padding:18px}
  .caja h2{margin:0 0 14px;font-size:11px;letter-spacing:2px;color:var(--suave);
           text-transform:uppercase;font-weight:600}

  /* ------------------------------------------------------- cuadro del actual */
  .tablero{display:flex;flex-direction:column;align-items:center;gap:6px}
  .aguja{position:relative;width:260px;height:260px}
  .aguja svg{position:absolute;inset:0}
  .centro{position:absolute;inset:0;display:flex;flex-direction:column;
          align-items:center;justify-content:center;text-align:center;gap:2px}
  .centro .ico{font-size:40px;line-height:1}
  .centro .nom{font-size:30px;font-weight:700;letter-spacing:.5px;color:var(--acento)}
  .centro .rot{font-size:11px;color:var(--suave);letter-spacing:2px;text-transform:uppercase}
  .desc{color:var(--suave);font-size:13px;text-align:center;max-width:380px;min-height:36px}

  .vecinos{display:flex;align-items:center;gap:10px;margin-top:6px;width:100%;
           justify-content:center;flex-wrap:wrap}
  .vecino{font-size:12px;color:var(--suave);background:#0c1320;border:1px solid var(--borde);
          border-radius:10px;padding:8px 12px;min-width:120px;text-align:center}
  .vecino b{display:block;color:var(--texto);font-size:14px;margin-top:2px}

  .mandos{display:flex;gap:12px;margin-top:14px;align-items:center;justify-content:center}
  .leva{background:#0d1623;border:1px solid var(--borde);color:var(--texto);
        font-size:20px;width:64px;height:52px;border-radius:14px;cursor:pointer;
        transition:.15s;display:grid;place-items:center}
  .leva:hover{border-color:var(--acento);color:var(--acento);transform:translateY(-2px)}
  .leva:active{transform:translateY(0) scale(.96)}
  .teclas{font-size:11px;color:var(--suave);text-align:center;margin-top:8px}

  /* ------------------------------------------------------------ medidores */
  .medidores{display:grid;gap:10px;width:100%;max-width:380px;margin-top:12px}
  .medidor{display:grid;grid-template-columns:86px 1fr 42px;align-items:center;gap:10px;font-size:11px}
  .medidor span{color:var(--suave);letter-spacing:1px;text-transform:uppercase}
  .barra{height:8px;background:#0a111d;border:1px solid var(--borde);border-radius:99px;overflow:hidden}
  .barra i{display:block;height:100%;border-radius:99px;transition:width .35s ease}
  .medidor em{font-style:normal;color:var(--texto);text-align:right;font-variant-numeric:tabular-nums}

  .ficha{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;width:100%;max-width:380px;margin-top:12px}
  .ficha div{background:#0a111d;border:1px solid var(--borde);border-radius:10px;padding:8px;text-align:center}
  .ficha small{display:block;color:var(--suave);font-size:10px;letter-spacing:1px;text-transform:uppercase}
  .ficha strong{font-size:12px;font-weight:600}

  /* ----------------------------------------------------- anillo de punteros */
  .anillo{display:grid;place-items:center}
  .anillo svg{width:100%;max-width:360px;height:auto;overflow:visible}
  .nodo{cursor:pointer}
  .leyenda{display:flex;gap:14px;flex-wrap:wrap;justify-content:center;
           font-size:11px;color:var(--suave);margin-top:10px}
  .leyenda i{display:inline-block;width:18px;height:3px;border-radius:2px;vertical-align:middle;margin-right:6px}

  /* ------------------------------------------------------- panel punteros */
  .punteros{font-family:Consolas,"Courier New",monospace;font-size:12.5px;line-height:1.9}
  .punteros div{background:#0a111d;border:1px solid var(--borde);border-left:3px solid var(--acento);
                border-radius:8px;padding:8px 12px;margin-bottom:8px;overflow-x:auto;white-space:nowrap}
  .punteros .cierre{border-left-color:var(--oro);color:var(--oro)}

  /* -------------------------------------------------------------- controles */
  .controles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
  label{display:block;font-size:10px;letter-spacing:1.4px;color:var(--suave);
        text-transform:uppercase;margin-bottom:5px}
  input,select{width:100%;background:#0a111d;border:1px solid var(--borde);color:var(--texto);
        border-radius:10px;padding:9px 10px;font-size:13px;font-family:inherit}
  input[type=color]{padding:3px;height:38px;cursor:pointer}
  input:focus,select:focus{outline:none;border-color:var(--acento)}
  .fila{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
  button.accion{flex:1;min-width:150px;border:none;border-radius:11px;padding:11px 14px;
        font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;transition:.15s}
  .verde{background:var(--acento);color:#05080e}
  .rojo{background:#2a1118;color:#ff6b7a;border:1px solid #58202c !important}
  .gris{background:#0d1623;color:var(--suave);border:1px solid var(--borde) !important}
  button.accion:hover{filter:brightness(1.12);transform:translateY(-1px)}

  .aviso{margin-top:12px;font-size:12px;color:#ff8f9a;min-height:16px}

  /* --------------------------------------------------------------- bitacora */
  .bitacora{font-family:Consolas,"Courier New",monospace;font-size:12px;color:var(--suave);
            max-height:170px;overflow:auto}
  .bitacora p{margin:0 0 6px;padding:5px 9px;background:#0a111d;border-radius:7px;
              border-left:2px solid var(--borde)}
  .bitacora p:first-child{border-left-color:var(--acento);color:var(--texto)}
  .vacio{color:var(--suave);font-size:13px;text-align:center;padding:26px 0}
</style>
</head>
<body>
<div class="marco">

  <header>
    <div class="logo">🚗</div>
    <div>
      <h1>Sistema de Infotenimiento y Modos de Conducci&oacute;n de un Veh&iacute;culo Inteligente</h1>
      <p>Lista Circular Doblemente Enlazada &middot; implementada desde cero en Python</p>
    </div>
    <div class="chip">ECU &middot; <span id="contador">0</span> modos</div>
  </header>

  <div class="rejilla">

    <!-- ============== PANEL IZQUIERDO: el modo actual ============== -->
    <section class="caja">
      <h2>Modo de conducci&oacute;n activo</h2>
      <div class="tablero">

        <div class="aguja">
          <svg viewBox="0 0 260 260">
            <circle cx="130" cy="130" r="112" fill="none" stroke="#1b2636" stroke-width="10"/>
            <circle id="arcoPotencia" cx="130" cy="130" r="112" fill="none"
                    stroke="var(--acento)" stroke-width="10" stroke-linecap="round"
                    stroke-dasharray="0 999" transform="rotate(-90 130 130)"
                    style="transition:stroke-dasharray .45s ease"/>
            <circle cx="130" cy="130" r="94" fill="none" stroke="#141d2b" stroke-width="1"/>
          </svg>
          <div class="centro">
            <div class="ico" id="icoActual">—</div>
            <div class="nom" id="nomActual">—</div>
            <div class="rot" id="rotActual">sin datos</div>
          </div>
        </div>

        <p class="desc" id="descActual"></p>

        <div class="vecinos">
          <div class="vecino">&#9664; anterior <b id="vecAnterior">—</b></div>
          <div class="vecino" style="border-color:var(--acento)">actual <b id="vecActual">—</b></div>
          <div class="vecino">siguiente &#9654; <b id="vecSiguiente">—</b></div>
        </div>

        <div class="mandos">
          <button class="leva" id="btnAnterior" title="Leva izquierda del volante">&#9664;</button>
          <button class="leva" id="btnSiguiente" title="Leva derecha del volante">&#9654;</button>
        </div>
        <div class="teclas">Tambi&eacute;n puedes usar las flechas &larr; y &rarr; del teclado</div>

        <div class="medidores">
          <div class="medidor"><span>Potencia</span><div class="barra"><i id="barPot"></i></div><em id="numPot">0%</em></div>
          <div class="medidor"><span>Consumo</span><div class="barra"><i id="barCon"></i></div><em id="numCon">0%</em></div>
        </div>

        <div class="ficha">
          <div><small>Direcci&oacute;n</small><strong id="fDireccion">—</strong></div>
          <div><small>Suspensi&oacute;n</small><strong id="fSuspension">—</strong></div>
          <div><small>Tracci&oacute;n</small><strong id="fTraccion">—</strong></div>
        </div>

      </div>
    </section>

    <!-- ============== PANEL DERECHO: los punteros ============== -->
    <section class="caja">
      <h2>Anillo de nodos &middot; naturaleza circular</h2>
      <div class="anillo">
        <svg id="svgAnillo" viewBox="-40 -40 400 400"></svg>
      </div>
      <div class="leyenda">
        <span><i style="background:#3a4a63"></i>siguiente (exterior, horario)</span>
        <span><i style="background:#2f5f52"></i>anterior (interior, antihorario)</span>
        <span><i style="background:var(--oro)"></i>cierre cola &harr; cabeza</span>
      </div>

      <h2 style="margin-top:18px">Estado de los punteros</h2>
      <div class="punteros" id="panelPunteros"></div>
    </section>
  </div>

  <!-- ============== CONTROLES ============== -->
  <div class="rejilla" style="margin-top:18px">
    <section class="caja">
      <h2>Agregar un modo a la lista</h2>
      <div class="controles">
        <div><label>Nombre</label><input id="inNombre" placeholder="Ej: Drift" maxlength="18"></div>
        <div><label>Icono</label><input id="inIcono" value="🎚️" maxlength="4"></div>
        <div><label>Color</label><input id="inColor" type="color" value="#00e0d0"></div>
        <div><label>Potencia %</label><input id="inPot" type="number" min="0" max="100" value="80"></div>
        <div><label>Consumo %</label><input id="inCon" type="number" min="0" max="100" value="70"></div>
        <div><label>Posici&oacute;n</label>
          <select id="inDonde">
            <option value="final">Al final (nueva cola)</option>
            <option value="actual">Despu&eacute;s del actual</option>
          </select>
        </div>
      </div>
      <div><label style="margin-top:12px">Descripci&oacute;n</label>
        <input id="inDesc" placeholder="Perfil definido por el conductor" maxlength="90"></div>
      <div class="fila">
        <button class="accion verde" id="btnInsertar">+ Insertar nodo</button>
      </div>
      <div class="aviso" id="aviso"></div>
    </section>

    <section class="caja">
      <h2>Operaciones sobre la lista</h2>
      <div class="fila" style="margin-top:0">
        <button class="accion rojo" id="btnEliminar">&#10005; Eliminar el modo actual</button>
        <button class="accion gris" id="btnReiniciar">&#10227; Reiniciar ECU</button>
      </div>
      <h2 style="margin-top:20px">Bit&aacute;cora de punteros</h2>
      <div class="bitacora" id="bitacora"></div>
    </section>
  </div>
</div>

<script>
/* =======================================================================
   1. UTILIDADES DE DIBUJO (geometria del anillo)
   ======================================================================= */
const CX = 160, CY = 160, R_EXT = 148, R_NODO = 118, R_INT = 92;

function punto(r, grados){                 // angulo en grados -> coordenada x,y
  const a = grados * Math.PI / 180;
  return [CX + r * Math.cos(a), CY + r * Math.sin(a)];
}
function arco(r, a1, a2){                  // path SVG de un arco a favor del reloj
  const [x1,y1] = punto(r,a1), [x2,y2] = punto(r,a2);
  const delta = ((a2 - a1) % 360 + 360) % 360;
  return `M ${x1} ${y1} A ${r} ${r} 0 ${delta>180?1:0} 1 ${x2} ${y2}`;
}
function flecha(r, grados, sentido, color){ // triangulo tangente al circulo
  const [x,y] = punto(r, grados);
  const giro = grados + (sentido > 0 ? 90 : -90);
  return `<polygon points="-5,-4 -5,4 5,0" fill="${color}"
           transform="translate(${x},${y}) rotate(${giro})"/>`;
}

/* =======================================================================
   2. PINTAR EL ANILLO DE NODOS
   ======================================================================= */
function dibujarAnillo(e){
  const svg = document.getElementById('svgAnillo');
  if(e.vacia){ svg.innerHTML = '<text x="160" y="165" fill="#8ba0bd" text-anchor="middle" font-size="14">Lista vacia</text>'; return; }

  const n = e.nodos.length;
  const paso = 360 / n;
  const angulo = i => -90 + i * paso;          // el primer nodo arriba
  let piezas = [];

  /* --- circulo base: el camino que recorren los punteros --- */
  piezas.push(`<circle cx="${CX}" cy="${CY}" r="${R_EXT}" fill="none" stroke="#3a4a63" stroke-width="2"/>`);
  piezas.push(`<circle cx="${CX}" cy="${CY}" r="${R_INT}" fill="none" stroke="#2f5f52" stroke-width="2" stroke-dasharray="5 6"/>`);

  /* --- tramo cola -> cabeza resaltado: aqui se CIERRA el circulo --- */
  if(n > 1){
    const iCola = e.nodos.findIndex(x => x.es_cola);
    const iCab  = e.nodos.findIndex(x => x.es_cabeza);
    piezas.push(`<path d="${arco(R_EXT, angulo(iCola), angulo(iCab))}" fill="none"
                   stroke="#ffc34d" stroke-width="4" stroke-linecap="round"/>`);
    piezas.push(`<path d="${arco(R_INT, angulo(iCola), angulo(iCab))}" fill="none"
                   stroke="#ffc34d" stroke-width="3" stroke-dasharray="4 5"/>`);
  }

  /* --- flechas de direccion en cada tramo --- */
  for(let i = 0; i < n; i++){
    const medio = angulo(i) + paso / 2;
    const esCierre = e.nodos[i].es_cola && n > 1;
    piezas.push(flecha(R_EXT, medio,  1, esCierre ? '#ffc34d' : '#5a6f90'));   // siguiente
    piezas.push(flecha(R_INT, medio, -1, esCierre ? '#ffc34d' : '#3f7f6d'));   // anterior
  }

  /* --- los nodos --- */
  e.nodos.forEach((nd, i) => {
    const [x,y] = punto(R_NODO, angulo(i));
    const radio = nd.es_actual ? 25 : 19;
    const borde = nd.es_actual ? nd.color : '#2a3a52';
    piezas.push(`<g class="nodo" data-nombre="${nd.nombre}">
        ${nd.es_actual ? `<circle cx="${x}" cy="${y}" r="${radio+7}" fill="none" stroke="${nd.color}" stroke-opacity=".35" stroke-width="2"/>` : ''}
        <circle cx="${x}" cy="${y}" r="${radio}" fill="#101925" stroke="${borde}" stroke-width="${nd.es_actual?3:2}"/>
        <text x="${x}" y="${y+6}" text-anchor="middle" font-size="${nd.es_actual?20:15}">${nd.icono}</text>
      </g>`);

    /* etiqueta con el nombre y su rol (CABEZA / COLA) */
    const [ex,ey] = punto(R_NODO + 44, angulo(i));
    const ancla = Math.cos(angulo(i)*Math.PI/180) > .2 ? 'start'
                : Math.cos(angulo(i)*Math.PI/180) < -.2 ? 'end' : 'middle';
    let rol = nd.es_cabeza ? 'CABEZA' : (nd.es_cola ? 'COLA' : '');
    piezas.push(`<text x="${ex}" y="${ey}" text-anchor="${ancla}" font-size="12"
                   fill="${nd.es_actual ? nd.color : '#8ba0bd'}" font-weight="${nd.es_actual?700:400}">${nd.nombre}</text>`);
    if(rol) piezas.push(`<text x="${ex}" y="${ey+13}" text-anchor="${ancla}" font-size="9"
                   fill="#ffc34d" letter-spacing="1.5">${rol}</text>`);
  });

  /* --- texto del centro: recordatorio de que no hay final --- */
  piezas.push(`<text x="${CX}" y="${CY-6}" text-anchor="middle" font-size="11" fill="#8ba0bd" letter-spacing="2">SIN FIN DE LISTA</text>`);
  piezas.push(`<text x="${CX}" y="${CY+12}" text-anchor="middle" font-size="11" fill="#8ba0bd">${n} nodo(s) enlazados</text>`);

  svg.innerHTML = piezas.join('');

  /* clic en un nodo = salto directo a ese modo */
  svg.querySelectorAll('.nodo').forEach(g => {
    g.onclick = () => enviar('/api/seleccionar', {nombre: g.dataset.nombre});
  });
}

/* =======================================================================
   3. PINTAR TODO EL TABLERO CON EL ESTADO QUE MANDO PYTHON
   ======================================================================= */
function pintar(e){
  document.getElementById('contador').textContent = e.tamanio;

  if(e.vacia){
    document.documentElement.style.setProperty('--acento', '#8ba0bd');
    document.getElementById('icoActual').textContent = '⚠';
    document.getElementById('nomActual').textContent = '—';
    document.getElementById('rotActual').textContent = 'lista vacia';
    document.getElementById('descActual').textContent = 'No hay modos en la ECU. Inserta uno nuevo o reinicia.';
    ['vecAnterior','vecActual','vecSiguiente','fDireccion','fSuspension','fTraccion']
      .forEach(id => document.getElementById(id).textContent = '—');
    document.getElementById('arcoPotencia').setAttribute('stroke-dasharray','0 999');
    document.getElementById('barPot').style.width = '0%';
    document.getElementById('barCon').style.width = '0%';
    document.getElementById('numPot').textContent = '0%';
    document.getElementById('numCon').textContent = '0%';
    document.getElementById('panelPunteros').innerHTML = '<div class="vacio">cabeza = cola = actual = None</div>';
    dibujarAnillo(e); pintarBitacora(e); return;
  }

  const a = e.actual;
  document.documentElement.style.setProperty('--acento', a.color);
  document.getElementById('icoActual').textContent = a.icono;
  document.getElementById('nomActual').textContent = a.nombre;
  document.getElementById('rotActual').textContent = 'modo activo';
  document.getElementById('descActual').textContent = a.descripcion;

  document.getElementById('vecAnterior').textContent  = e.anterior;
  document.getElementById('vecActual').textContent    = a.nombre;
  document.getElementById('vecSiguiente').textContent = e.siguiente;

  /* arco de potencia: 2*pi*112 = 703.7 de perimetro */
  const total = 2 * Math.PI * 112;
  document.getElementById('arcoPotencia')
          .setAttribute('stroke-dasharray', `${total * a.potencia / 100} ${total}`);

  document.getElementById('barPot').style.width = a.potencia + '%';
  document.getElementById('barPot').style.background = a.color;
  document.getElementById('barCon').style.width = a.consumo + '%';
  document.getElementById('barCon').style.background = a.consumo > 70 ? '#ff6b7a' : '#39d98a';
  document.getElementById('numPot').textContent = a.potencia + '%';
  document.getElementById('numCon').textContent = a.consumo + '%';

  document.getElementById('fDireccion').textContent  = a.direccion;
  document.getElementById('fSuspension').textContent = a.suspension;
  document.getElementById('fTraccion').textContent   = a.traccion;

  /* panel de punteros en crudo, para que se vea la estructura real */
  document.getElementById('panelPunteros').innerHTML = `
    <div>cabeza &rarr; <b>${e.cabeza}</b> &nbsp;|&nbsp; cola &rarr; <b>${e.cola}</b> &nbsp;|&nbsp; tamanio = ${e.tamanio}</div>
    <div>actual.anterior  &rarr; ${e.anterior}</div>
    <div>actual           &rarr; ${a.nombre}</div>
    <div>actual.siguiente &rarr; ${e.siguiente}</div>
    <div class="cierre">cola(${e.cola}).siguiente &rarr; cabeza(${e.cabeza})</div>
    <div class="cierre">cabeza(${e.cabeza}).anterior &rarr; cola(${e.cola})</div>
    <div style="border-left-color:#2f5f52;white-space:normal">${e.dibujo}</div>`;

  dibujarAnillo(e);
  pintarBitacora(e);
}

function pintarBitacora(e){
  const caja = document.getElementById('bitacora');
  caja.innerHTML = (e.bitacora && e.bitacora.length)
    ? e.bitacora.map(t => `<p>${t}</p>`).join('')
    : '<p>Sin operaciones todavia. Usa las levas del volante.</p>';
}

/* =======================================================================
   4. CONVERSACION CON EL BACKEND
   ======================================================================= */
async function enviar(ruta, cuerpo){
  const aviso = document.getElementById('aviso');
  aviso.textContent = '';
  try{
    const r = await fetch(ruta, {
      method: cuerpo === undefined ? 'GET' : 'POST',
      headers: {'Content-Type':'application/json'},
      body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo)
    });
    const datos = await r.json();
    if(!r.ok){ aviso.textContent = datos.error || 'Operacion rechazada'; return; }
    pintar(datos);
  }catch(err){
    aviso.textContent = 'No se pudo contactar la ECU: ' + err.message;
  }
}

/* =======================================================================
   5. CABLEADO DE LOS BOTONES
   ======================================================================= */
document.getElementById('btnSiguiente').onclick = () => enviar('/api/siguiente', {});
document.getElementById('btnAnterior').onclick  = () => enviar('/api/anterior', {});
document.getElementById('btnEliminar').onclick  = () => enviar('/api/eliminar', {});
document.getElementById('btnReiniciar').onclick = () => enviar('/api/reiniciar', {});

document.getElementById('btnInsertar').onclick = () => {
  enviar('/api/insertar', {
    nombre: document.getElementById('inNombre').value,
    icono: document.getElementById('inIcono').value,
    color: document.getElementById('inColor').value,
    descripcion: document.getElementById('inDesc').value,
    potencia: Number(document.getElementById('inPot').value),
    consumo: Number(document.getElementById('inCon').value),
    despues_del_actual: document.getElementById('inDonde').value === 'actual'
  });
  document.getElementById('inNombre').value = '';
  document.getElementById('inDesc').value = '';
};

/* las levas del volante tambien responden al teclado */
document.addEventListener('keydown', ev => {
  if(ev.target.tagName === 'INPUT' || ev.target.tagName === 'SELECT') return;
  if(ev.key === 'ArrowRight') enviar('/api/siguiente', {});
  if(ev.key === 'ArrowLeft')  enviar('/api/anterior', {});
});

/* arranque: pedir el estado inicial a Python */
enviar('/api/estado');
</script>
</body>
</html>
"""


# ==============================================================================
# BLOQUE 7 - ARRANQUE: demostracion por consola y puesta en marcha del servidor
# ==============================================================================
def demostracion_consola() -> None:
    """Prueba la estructura sin interfaz grafica, para verla funcionar en texto."""
    print("=" * 72)
    print(" DEMOSTRACION DE LA LISTA CIRCULAR DOBLEMENTE ENLAZADA")
    print("=" * 72)
    print(" Lista inicial :", ECU)
    print(" Actual        :", ECU.mostrar_actual())
    print(" Cabeza / Cola :", ECU.cabeza.dato.nombre, "/", ECU.cola.dato.nombre)

    print("\n Avanzando 4 veces con avanzar_siguiente():")
    for _ in range(4):
        print("   ->", ECU.avanzar_siguiente().nombre)
    print("   (se paso de Individual a Eco sin un solo 'if': eso es la circularidad)")

    print("\n Retrocediendo 2 veces con retroceder_anterior():")
    for _ in range(2):
        print("   <-", ECU.retroceder_anterior().nombre)

    print("\n Insertando 'Drift' despues del actual y eliminando 'Off-Road':")
    ECU.insertar(ModoConduccion(nombre="Drift", icono="💨", color="#ff8a3d",
                                descripcion="Par total al eje trasero.",
                                potencia=98, consumo=95),
                 despues_del_actual=True)
    ECU.eliminar("Off-Road")
    print("  ", ECU)
    print("   Cabeza:", ECU.cabeza.dato.nombre, "| Cola:", ECU.cola.dato.nombre,
          "| Tamanio:", len(ECU))
    print("   Comprobacion del cierre del circulo:")
    print("     cola.siguiente  ==", ECU.cola.siguiente.dato.nombre,
          "(deberia ser la cabeza)")
    print("     cabeza.anterior ==", ECU.cabeza.anterior.dato.nombre,
          "(deberia ser la cola)")

    print("\n Nombres via obtener_todos():",
          [m.nombre for m in ECU.obtener_todos()])
    print("=" * 72)


if __name__ == "__main__":
    import webbrowser

    demostracion_consola()

    # Se vuelve a crear la lista para que el tablero arranque de fabrica.
    ECU = crear_lista_inicial()
    BITACORA.clear()

    print("\n Tablero disponible en:  http://127.0.0.1:5000")
    print(" Para detener el servidor pulsa Ctrl + C\n")
    try:
        webbrowser.open("http://127.0.0.1:5000")
    except Exception:
        pass
    app.run(host="127.0.0.1", port=5000, debug=False)
