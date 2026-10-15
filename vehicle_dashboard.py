# -*- coding: utf-8 -*-
"""
===============================================================================
 WORKSHOP: CIRCULAR DOUBLY LINKED LISTS
 Case study: Infotainment and Driving Mode System of a Smart Vehicle
===============================================================================

 NOTE ON LANGUAGE
 ----------------
 The code is written in English (classes, methods, variables, comments and API
 keys). Every string the driver actually reads on screen stays in Spanish,
 because the dashboard is the user-facing interface of the vehicle.

 FILE LAYOUT
 -----------
   BLOCK 1 : DrivingMode ................ the payload stored inside each node
   BLOCK 2 : Node ....................... the cell holding the prev/next pointers
   BLOCK 3 : CircularDoublyLinkedList ... the data structure, built from scratch
   BLOCK 4 : factory data ............... the 5 driving modes shipped with the car
   BLOCK 5 : Flask backend .............. REST API that exposes the list
   BLOCK 6 : HTML/CSS/JS frontend ....... the digital dashboard of the car
   BLOCK 7 : entry point ................ console demo + web server


 WHY A CIRCULAR DOUBLY LINKED LIST FITS THE AUTOMOTIVE INDUSTRY
 --------------------------------------------------------------
 The driver only has TWO physical inputs available: a paddle/button meaning
 "next" and another one meaning "previous" (or a dial that turns both ways).
 They cannot type an index or pick a position: they can only step forward or
 backward. That interface demands exactly three properties:

   1) CIRCULAR -> The driver must never hit an "end of list". If the car is in
      Individual (the last mode) and the right paddle is pressed again, Eco has
      to show up. A plain list would have to ask on every press "did I reach the
      end? then wrap around to the beginning". Here the last node points to the
      first one, so that special case DISAPPEARS: the walk is endless without a
      single 'if'.

   2) DOUBLY LINKED -> The left paddle has to step back one mode. With forward
      pointers only, finding the previous neighbour means walking the whole
      list: O(n) and, on a steering wheel, a delay the driver can feel. With the
      'prev' pointer, stepping back costs O(1), exactly like stepping forward.
      Symmetric cost means a symmetric driving experience.

   3) CHEAP INSERTION / DELETION -> A user adds the "Individual 2" profile, the
      workshop disables Off-Road on a car without all-wheel drive, or a radio
      station gets saved or erased. In a linked list that is four pointers being
      rewired, O(1), without shifting the remaining elements the way an array
      would force us to.

 Because of all that, every paddle press is resolved in CONSTANT TIME with a
 single instruction: self.current = self.current.next (or .prev). That is the
 heart of the workshop.
"""

from dataclasses import dataclass, asdict


# ==============================================================================
# BLOCK 1 - THE PAYLOAD: one driving mode of the vehicle
# ==============================================================================
@dataclass
class DrivingMode:
    """Settings the on-board computer applies when a mode is selected.

    This is only the CONTENT (the payload). It knows nothing about pointers or
    lists: that is the Node's responsibility. Keeping payload and node apart is
    the single responsibility principle at work: if the payload becomes a
    'RadioStation' tomorrow, the circular list keeps working untouched.

    The textual fields stay in Spanish on purpose: they are printed straight
    onto the dashboard the driver looks at.
    """
    name: str                        # label shown on the dashboard
    icon: str = "*"                  # emoji identifying the mode
    color: str = "#39d98a"           # accent color of the dashboard (hex)
    description: str = ""            # short explanatory sentence (Spanish)
    power: int = 50                  # 0-100, throttle response
    consumption: int = 50            # 0-100, estimated fuel consumption
    steering: str = "Normal"         # steering assistance (Spanish)
    suspension: str = "Normal"       # suspension stiffness (Spanish)
    drivetrain: str = "Delantera"    # torque split across the wheels (Spanish)

    def to_dict(self) -> dict:
        """Turn the payload into a dict so it can be shipped to the browser."""
        return asdict(self)


# ==============================================================================
# BLOCK 2 - THE NODE: payload + two pointers
# ==============================================================================
class Node:
    """One cell of the list.

    It holds the payload and TWO references:
        next -> the cell on its right
        prev -> the cell on its left

    In a circular list they are NEVER left as None after an insertion: if the
    list holds a single node, that node points to itself in both directions.
    """

    def __init__(self, data: DrivingMode):
        self.data = data      # the payload (a DrivingMode)
        self.next = None      # wired up when the node joins the list
        self.prev = None      # wired up when the node joins the list

    def __repr__(self) -> str:
        # Handy representation while debugging from the console.
        previous = self.prev.data.name if self.prev else "None"
        following = self.next.data.name if self.next else "None"
        return f"[{previous}] <- ({self.data.name}) -> [{following}]"


# ==============================================================================
# BLOCK 3 - THE DATA STRUCTURE, BUILT FROM SCRATCH
# ==============================================================================
class CircularDoublyLinkedList:
    """Circular doubly linked list implemented by hand.

    No native Python list is used as the main structure: the whole storage lives
    inside the Node objects and their pointers. The only Python lists around are
    OUTPUT ones (get_all / snapshot), that is, temporary photographs taken to
    draw the interface.

    Control attributes:
        head    -> first node of the list    (the "Eco" mode)
        tail    -> last node of the list     (the "Individual" mode)
        current -> node the driver has selected right now
        size    -> number of nodes, so we never have to count them again
    """

    # ----------------------------------------------------------- construction
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0

    # ------------------------------------------------------------- inspection
    def is_empty(self) -> bool:
        """True when there is no node at all. First question of almost every method."""
        return self.head is None

    def __len__(self) -> int:
        """Allows len(list). Returns the internal counter: O(1)."""
        return self.size

    def find(self, name: str):
        """Return the Node whose payload is called 'name', or None if missing.

        Walks the list exactly ONE lap. The loop does not stop on "node is None"
        the way a plain list would, but on "I came back to the head": that is how
        the infinite loop caused by circularity is avoided.
        """
        if self.is_empty():
            return None
        node = self.head
        while True:
            if node.data.name.lower() == name.strip().lower():
                return node
            node = node.next
            if node is self.head:        # we completed a full lap
                return None

    # ---------------------------------------------------------------- insert
    def insert(self, data: DrivingMode, after_current: bool = False):
        """Add a new mode to the list and return the Node that was created.

        after_current = False -> append it at the end (behind the tail).
        after_current = True  -> splice it right after the current mode, which is
                                 what feels natural when the driver customises a
                                 profile "right here".

        Cost O(1): nothing is traversed, only pointers are rewired.
        """
        new_node = Node(data)

        # CASE A: the list was empty. The node is head, tail and current all at
        # once, and the circle is closed by pointing it to itself both ways.
        if self.is_empty():
            new_node.next = new_node
            new_node.prev = new_node
            self.head = new_node
            self.tail = new_node
            self.current = new_node
            self.size += 1
            return new_node

        # CASE B: insert right after the current node.
        if after_current:
            left = self.current                  # neighbour on the left
            right = self.current.next            # neighbour on the right
            new_node.prev = left                 # 1. the new node looks left
            new_node.next = right                # 2. the new node looks right
            left.next = new_node                 # 3. the left one adopts it
            right.prev = new_node                # 4. the right one adopts it
            if left is self.tail:                # inserted behind the tail?
                self.tail = new_node             # then the new node is the tail
            self.size += 1
            return new_node

        # CASE C: append at the end (between the old tail and the head).
        new_node.prev = self.tail                # 1. the tail sits behind it
        new_node.next = self.head                # 2. the head sits ahead of it
        self.tail.next = new_node                # 3. the tail now points to it
        self.head.prev = new_node                # 4. the head steps back to it
        self.tail = new_node                     # 5. the new node is the tail
        self.size += 1
        return new_node

    # ---------------------------------------------------------------- remove
    def remove(self, name: str = None):
        """Drop a node and return its payload (or None when there is nothing to drop).

        With no argument it removes the CURRENT mode, which is the real gesture
        on the dashboard: "delete the one I am looking at". With a name, it
        removes that specific one.
        """
        if self.is_empty():
            return None

        target = self.current if name is None else self.find(name)
        if target is None:
            return None

        data = target.data

        # CASE A: it was the only node -> the list becomes completely empty.
        if self.size == 1:
            self.head = None
            self.tail = None
            self.current = None
            self.size = 0
            return data

        # CASE B: there are more nodes -> stitch the gap by joining both neighbours.
        left = target.prev
        right = target.next
        left.next = right              # the left one jumps over the gap
        right.prev = left              # and so does the right one

        # When an endpoint is removed, that endpoint moves to its neighbour.
        if target is self.head:
            self.head = right
        if target is self.tail:
            self.tail = left
        # If the driver was looking at the deleted mode, the dashboard moves on
        # to the next one: it is never left without an active mode.
        if target is self.current:
            self.current = right

        # Isolate the removed node so the garbage collector can free it.
        target.next = None
        target.prev = None
        self.size -= 1
        return data

    # ------------------------------------------------ steering wheel paddles
    def move_next(self):
        """Right paddle: step to the following mode. O(1).

        The benefit of circularity shows up here: there is no need to check
        whether we reached the end, because tail.next IS the head already.
        """
        if self.is_empty():
            return None
        self.current = self.current.next
        return self.current.data

    def move_previous(self):
        """Left paddle: step back to the previous mode. O(1).

        Thanks to the 'prev' pointer, stepping back costs the same as stepping
        forward; and since head.prev is the tail, Eco jumps straight to Individual.
        """
        if self.is_empty():
            return None
        self.current = self.current.prev
        return self.current.data

    def select(self, name: str):
        """Jump straight to a mode (the driver taps its icon on the screen)."""
        node = self.find(name)
        if node is None:
            return None
        self.current = node
        return node.data

    # ----------------------------------------------------------------- output
    def show_current(self) -> str:
        """Text of the active mode, exactly as the dashboard would print it.

        It also shows both neighbours so the double link stays visible.
        The returned text is Spanish: it is read by the driver.
        """
        if self.is_empty():
            return "Sin modos cargados en la ECU"
        previous = self.current.prev.data.name
        active = self.current.data.name
        following = self.current.next.data.name
        return f"<< {previous}  |  [ {active} ]  |  {following} >>"

    def get_all(self) -> list:
        """Python list with every payload, ordered from the head.

        IMPORTANT: this list is just an output copy used to draw the interface;
        the real storage is still the chain of nodes.
        """
        items = []
        if self.is_empty():
            return items
        node = self.head
        while True:
            items.append(node.data)
            node = node.next
            if node is self.head:       # circular stop condition
                break
        return items

    def __iter__(self):
        """Allows walking the list with a for loop, taking a single lap."""
        return iter(self.get_all())

    def __str__(self) -> str:
        """One-line drawing of the list, with the current mode in brackets."""
        if self.is_empty():
            return "(lista vacia)"
        pieces = []
        for mode in self.get_all():
            if self.current and mode.name == self.current.data.name:
                pieces.append(f"[{mode.name}]")
            else:
                pieces.append(mode.name)
        return "... <-> " + " <-> ".join(pieces) + " <-> ..."

    # ------------------------------------------------ photograph for the UI
    def snapshot(self) -> dict:
        """Pack EVERYTHING the dashboard needs to know, as JSON-ready data.

        For every node the names of both neighbours are sent, so the browser can
        draw the real pointer arrows instead of guessing them.
        """
        nodes = []
        if not self.is_empty():
            node = self.head
            while True:
                item = node.data.to_dict()
                item["prev"] = node.prev.data.name
                item["next"] = node.next.data.name
                item["is_head"] = node is self.head
                item["is_tail"] = node is self.tail
                item["is_current"] = node is self.current
                nodes.append(item)
                node = node.next
                if node is self.head:
                    break

        return {
            "empty": self.is_empty(),
            "size": self.size,
            "head": self.head.data.name if self.head else None,
            "tail": self.tail.data.name if self.tail else None,
            "current": self.current.data.to_dict() if self.current else None,
            "prev": self.current.prev.data.name if self.current else None,
            "next": self.current.next.data.name if self.current else None,
            "nodes": nodes,
            "text": self.show_current(),
            "diagram": str(self),
        }


# ==============================================================================
# BLOCK 4 - FACTORY DATA: the 5 modes the vehicle ships with
# ==============================================================================
# The texts stay in Spanish because they are printed on the dashboard.
FACTORY_MODES = [
    DrivingMode(
        name="Eco",
        icon="🌿",
        color="#39d98a",
        description="Maxima autonomia. Suaviza el acelerador y corta el par innecesario.",
        power=35, consumption=22,
        steering="Ligera", suspension="Blanda", drivetrain="Delantera",
    ),
    DrivingMode(
        name="Confort",
        icon="🛋️",
        color="#4aa8ff",
        description="Ajuste equilibrado para ciudad y carretera. Es el modo por defecto.",
        power=55, consumption=45,
        steering="Asistida", suspension="Adaptativa", drivetrain="Delantera",
    ),
    DrivingMode(
        name="Sport",
        icon="🏁",
        color="#ff4d5a",
        description="Respuesta inmediata, cambios tardios y escape activo.",
        power=92, consumption=85,
        steering="Firme", suspension="Rigida", drivetrain="Trasera 70/30",
    ),
    DrivingMode(
        name="Off-Road",
        icon="⛰️",
        color="#f0a63c",
        description="Control de descenso, bloqueo de diferencial y altura elevada.",
        power=70, consumption=78,
        steering="Pesada", suspension="Elevada", drivetrain="Integral 50/50",
    ),
    DrivingMode(
        name="Individual",
        icon="🎛️",
        color="#b07cff",
        description="Perfil libre del conductor. Guarda su combinacion favorita.",
        power=65, consumption=60,
        steering="Personalizada", suspension="Personalizada", drivetrain="Configurable",
    ),
]


def create_initial_list() -> CircularDoublyLinkedList:
    """Build the circular doubly linked list holding the factory modes.

    Appends them one by one; once finished, Individual.next == Eco and
    Eco.prev == Individual, which means the circle is already closed.
    """
    modes = CircularDoublyLinkedList()
    for mode in FACTORY_MODES:
        # A COPY of the payload is inserted so a reset never drags old changes.
        modes.insert(DrivingMode(**mode.to_dict()))
    modes.select("Confort")   # the car boots in Confort, like real vehicles do
    return modes


# ==============================================================================
# BLOCK 5 - BACKEND: Flask server exposing the list as a REST API
# ==============================================================================
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# Single instance of the structure: it represents the memory of the car's ECU.
ECU = create_initial_list()

# Pointer activity log. It is kept OUTSIDE the class so the data structure stays
# pure (single responsibility): the list links nodes, the application records
# what the driver did. Its messages are Spanish because they are displayed.
EVENT_LOG = []


def log_event(message: str) -> None:
    """Store one line in the log, keeping only the 12 most recent ones."""
    EVENT_LOG.insert(0, message)
    del EVENT_LOG[12:]


def json_response():
    """Return the full state of the list plus the event log, as JSON."""
    payload = ECU.snapshot()
    payload["log"] = list(EVENT_LOG)
    return jsonify(payload)


@app.get("/api/state")
def api_state():
    """Current photograph. The browser asks for it when the page loads."""
    return json_response()


@app.post("/api/next")
def api_next():
    """Right paddle: current = current.next."""
    previous_name = ECU.current.data.name if ECU.current else "-"
    mode = ECU.move_next()
    if mode:
        log_event(f"▶  {previous_name}.siguiente  ->  {mode.name}")
    return json_response()


@app.post("/api/previous")
def api_previous():
    """Left paddle: current = current.prev."""
    previous_name = ECU.current.data.name if ECU.current else "-"
    mode = ECU.move_previous()
    if mode:
        log_event(f"◀  {previous_name}.anterior  ->  {mode.name}")
    return json_response()


@app.post("/api/select")
def api_select():
    """Direct jump triggered by tapping a node of the ring."""
    name = (request.json or {}).get("name", "")
    mode = ECU.select(name)
    if mode:
        log_event(f"⦿  salto directo  ->  {mode.name}")
    return json_response()


@app.post("/api/insert")
def api_insert():
    """Create a brand new mode and link it into the list.

    The dashboard form sends name, icon, color, description, power, consumption
    and where to place it (at the end or right after the current mode).
    """
    body = request.json or {}
    name = str(body.get("name", "")).strip()
    if not name:
        return jsonify({"error": "El nombre del modo no puede estar vacio"}), 400
    if ECU.find(name):
        return jsonify({"error": f"El modo '{name}' ya existe en la lista"}), 400

    new_mode = DrivingMode(
        name=name,
        icon=str(body.get("icon") or "🎚️")[:4],
        color=str(body.get("color") or "#00e0d0"),
        description=str(body.get("description") or "Modo definido por el conductor."),
        power=max(0, min(100, int(body.get("power", 50)))),
        consumption=max(0, min(100, int(body.get("consumption", 50)))),
        steering="Personalizada",
        suspension="Personalizada",
        drivetrain="Configurable",
    )
    after_current = bool(body.get("after_current", False))
    ECU.insert(new_mode, after_current=after_current)
    where = "despues del actual" if after_current else "al final (nueva cola)"
    log_event(f"+  insertado '{name}' {where} | 4 punteros reconectados")
    return json_response()


@app.post("/api/remove")
def api_remove():
    """Remove the current mode (or one by name) and stitch the gap."""
    name = (request.json or {}).get("name") or None
    if ECU.is_empty():
        return jsonify({"error": "La lista ya esta vacia"}), 400
    data = ECU.remove(name)
    if data is None:
        return jsonify({"error": "No se encontro ese modo"}), 400
    log_event(f"-  eliminado '{data.name}' | sus vecinos quedaron unidos")
    return json_response()


@app.post("/api/reset")
def api_reset():
    """Restore the 5 factory modes (the ECU RESET button)."""
    global ECU
    ECU = create_initial_list()
    EVENT_LOG.clear()
    log_event("⟲  ECU reiniciada con los 5 modos de fabrica")
    return json_response()


@app.get("/")
def index():
    """Serve the dashboard. It is sent as plain HTML text, without Jinja
    templates, because every piece of data arrives later by fetch to /api/*."""
    return Response(DASHBOARD_HTML, mimetype="text/html")


# ==============================================================================
# BLOCK 6 - FRONTEND: the digital dashboard of the car (HTML + CSS + JS)
# ==============================================================================
# It lives inside a text string so the whole workshop fits in a single .py file.
# The browser receives this string as-is and then talks to the backend through
# fetch() against the /api/* routes.
#
# Markup, selectors and script are English; every visible label is Spanish,
# because this is the interface the driver reads.
DASHBOARD_HTML = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sistema de Infotenimiento y Modos de Conducción de un Vehículo Inteligente</title>
<style>
  :root{
    --accent:#4aa8ff;
    --bg:#070a10;
    --panel:#101722;
    --panel2:#161f2e;
    --border:#223044;
    --text:#e7eef8;
    --muted:#8ba0bd;
    --gold:#ffc34d;
  }
  *{box-sizing:border-box}
  body{
    margin:0; padding:24px 18px 48px;
    background:
      radial-gradient(900px 500px at 50% -10%, rgba(74,168,255,.10), transparent 60%),
      var(--bg);
    color:var(--text);
    font-family:"Segoe UI",system-ui,-apple-system,Roboto,sans-serif;
    min-height:100vh;
  }
  .frame{max-width:1180px;margin:0 auto}

  /* ----------------------------------------------------- vehicle header bar */
  header{display:flex;flex-wrap:wrap;align-items:center;gap:14px;
         border-bottom:1px solid var(--border);padding-bottom:14px;margin-bottom:22px}
  header .logo{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;
         background:linear-gradient(145deg,var(--accent),rgba(0,0,0,.4));font-size:22px}
  header h1{font-size:17px;margin:0;letter-spacing:.2px;font-weight:600}
  header p{margin:2px 0 0;font-size:12px;color:var(--muted)}
  .badge{margin-left:auto;font-size:11px;letter-spacing:1.5px;color:var(--muted);
        border:1px solid var(--border);border-radius:999px;padding:6px 12px;text-transform:uppercase}

  /* ------------------------------------------------------------------- grid */
  .grid{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:18px}
  @media (max-width:900px){.grid{grid-template-columns:1fr}}
  .card{background:linear-gradient(180deg,var(--panel),var(--panel2));
        border:1px solid var(--border);border-radius:18px;padding:18px}
  .card h2{margin:0 0 14px;font-size:11px;letter-spacing:2px;color:var(--muted);
           text-transform:uppercase;font-weight:600}

  /* --------------------------------------------------------- current mode */
  .dashboard{display:flex;flex-direction:column;align-items:center;gap:6px}
  .gauge{position:relative;width:260px;height:260px}
  .gauge svg{position:absolute;inset:0}
  .center{position:absolute;inset:0;display:flex;flex-direction:column;
          align-items:center;justify-content:center;text-align:center;gap:2px}
  .center .icon{font-size:40px;line-height:1}
  .center .name{font-size:30px;font-weight:700;letter-spacing:.5px;color:var(--accent)}
  .center .tag{font-size:11px;color:var(--muted);letter-spacing:2px;text-transform:uppercase}
  .desc{color:var(--muted);font-size:13px;text-align:center;max-width:380px;min-height:36px}

  .neighbors{display:flex;align-items:center;gap:10px;margin-top:6px;width:100%;
           justify-content:center;flex-wrap:wrap}
  .neighbor{font-size:12px;color:var(--muted);background:#0c1320;border:1px solid var(--border);
          border-radius:10px;padding:8px 12px;min-width:120px;text-align:center}
  .neighbor b{display:block;color:var(--text);font-size:14px;margin-top:2px}

  .paddles{display:flex;gap:12px;margin-top:14px;align-items:center;justify-content:center}
  .paddle{background:#0d1623;border:1px solid var(--border);color:var(--text);
        font-size:20px;width:64px;height:52px;border-radius:14px;cursor:pointer;
        transition:.15s;display:grid;place-items:center}
  .paddle:hover{border-color:var(--accent);color:var(--accent);transform:translateY(-2px)}
  .paddle:active{transform:translateY(0) scale(.96)}
  .keys{font-size:11px;color:var(--muted);text-align:center;margin-top:8px}

  /* ----------------------------------------------------------------- meters */
  .meters{display:grid;gap:10px;width:100%;max-width:380px;margin-top:12px}
  .meter{display:grid;grid-template-columns:86px 1fr 42px;align-items:center;gap:10px;font-size:11px}
  .meter span{color:var(--muted);letter-spacing:1px;text-transform:uppercase}
  .bar{height:8px;background:#0a111d;border:1px solid var(--border);border-radius:99px;overflow:hidden}
  .bar i{display:block;height:100%;border-radius:99px;transition:width .35s ease}
  .meter em{font-style:normal;color:var(--text);text-align:right;font-variant-numeric:tabular-nums}

  .specs{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;width:100%;max-width:380px;margin-top:12px}
  .specs div{background:#0a111d;border:1px solid var(--border);border-radius:10px;padding:8px;text-align:center}
  .specs small{display:block;color:var(--muted);font-size:10px;letter-spacing:1px;text-transform:uppercase}
  .specs strong{font-size:12px;font-weight:600}

  /* ------------------------------------------------------------ pointer ring */
  .ring{display:grid;place-items:center}
  .ring svg{width:100%;max-width:360px;height:auto;overflow:visible}
  .node{cursor:pointer}
  .legend{display:flex;gap:14px;flex-wrap:wrap;justify-content:center;
           font-size:11px;color:var(--muted);margin-top:10px}
  .legend i{display:inline-block;width:18px;height:3px;border-radius:2px;vertical-align:middle;margin-right:6px}

  /* ----------------------------------------------------------- pointer panel */
  .pointers{font-family:Consolas,"Courier New",monospace;font-size:12.5px;line-height:1.9}
  .pointers div{background:#0a111d;border:1px solid var(--border);border-left:3px solid var(--accent);
                border-radius:8px;padding:8px 12px;margin-bottom:8px;overflow-x:auto;white-space:nowrap}
  .pointers .closing{border-left-color:var(--gold);color:var(--gold)}

  /* --------------------------------------------------------------- controls */
  .inputs{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
  label{display:block;font-size:10px;letter-spacing:1.4px;color:var(--muted);
        text-transform:uppercase;margin-bottom:5px}
  input,select{width:100%;background:#0a111d;border:1px solid var(--border);color:var(--text);
        border-radius:10px;padding:9px 10px;font-size:13px;font-family:inherit}
  input[type=color]{padding:3px;height:38px;cursor:pointer}
  input:focus,select:focus{outline:none;border-color:var(--accent)}
  .row{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
  button.action{flex:1;min-width:150px;border:none;border-radius:11px;padding:11px 14px;
        font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;transition:.15s}
  .green{background:var(--accent);color:#05080e}
  .red{background:#2a1118;color:#ff6b7a;border:1px solid #58202c !important}
  .gray{background:#0d1623;color:var(--muted);border:1px solid var(--border) !important}
  button.action:hover{filter:brightness(1.12);transform:translateY(-1px)}

  .notice{margin-top:12px;font-size:12px;color:#ff8f9a;min-height:16px}

  /* -------------------------------------------------------------- event log */
  .log{font-family:Consolas,"Courier New",monospace;font-size:12px;color:var(--muted);
            max-height:170px;overflow:auto}
  .log p{margin:0 0 6px;padding:5px 9px;background:#0a111d;border-radius:7px;
              border-left:2px solid var(--border)}
  .log p:first-child{border-left-color:var(--accent);color:var(--text)}
  .empty{color:var(--muted);font-size:13px;text-align:center;padding:26px 0}
</style>
</head>
<body>
<div class="frame">

  <header>
    <div class="logo">🚗</div>
    <div>
      <h1>Sistema de Infotenimiento y Modos de Conducci&oacute;n de un Veh&iacute;culo Inteligente</h1>
      <p>Lista Circular Doblemente Enlazada &middot; implementada desde cero en Python</p>
    </div>
    <div class="badge">ECU &middot; <span id="modeCount">0</span> modos</div>
  </header>

  <div class="grid">

    <!-- ============== LEFT PANEL: the current mode ============== -->
    <section class="card">
      <h2>Modo de conducci&oacute;n activo</h2>
      <div class="dashboard">

        <div class="gauge">
          <svg viewBox="0 0 260 260">
            <circle cx="130" cy="130" r="112" fill="none" stroke="#1b2636" stroke-width="10"/>
            <circle id="powerArc" cx="130" cy="130" r="112" fill="none"
                    stroke="var(--accent)" stroke-width="10" stroke-linecap="round"
                    stroke-dasharray="0 999" transform="rotate(-90 130 130)"
                    style="transition:stroke-dasharray .45s ease"/>
            <circle cx="130" cy="130" r="94" fill="none" stroke="#141d2b" stroke-width="1"/>
          </svg>
          <div class="center">
            <div class="icon" id="currentIcon">—</div>
            <div class="name" id="currentName">—</div>
            <div class="tag" id="currentTag">sin datos</div>
          </div>
        </div>

        <p class="desc" id="currentDesc"></p>

        <div class="neighbors">
          <div class="neighbor">&#9664; anterior <b id="prevName">—</b></div>
          <div class="neighbor" style="border-color:var(--accent)">actual <b id="activeName">—</b></div>
          <div class="neighbor">siguiente &#9654; <b id="nextName">—</b></div>
        </div>

        <div class="paddles">
          <button class="paddle" id="btnPrev" title="Leva izquierda del volante">&#9664;</button>
          <button class="paddle" id="btnNext" title="Leva derecha del volante">&#9654;</button>
        </div>
        <div class="keys">Tambi&eacute;n puedes usar las flechas &larr; y &rarr; del teclado</div>

        <div class="meters">
          <div class="meter"><span>Potencia</span><div class="bar"><i id="powerBar"></i></div><em id="powerNum">0%</em></div>
          <div class="meter"><span>Consumo</span><div class="bar"><i id="consumptionBar"></i></div><em id="consumptionNum">0%</em></div>
        </div>

        <div class="specs">
          <div><small>Direcci&oacute;n</small><strong id="specSteering">—</strong></div>
          <div><small>Suspensi&oacute;n</small><strong id="specSuspension">—</strong></div>
          <div><small>Tracci&oacute;n</small><strong id="specDrivetrain">—</strong></div>
        </div>

      </div>
    </section>

    <!-- ============== RIGHT PANEL: the pointers ============== -->
    <section class="card">
      <h2>Anillo de nodos &middot; naturaleza circular</h2>
      <div class="ring">
        <svg id="ringSvg" viewBox="-40 -40 400 400"></svg>
      </div>
      <div class="legend">
        <span><i style="background:#3a4a63"></i>siguiente (exterior, horario)</span>
        <span><i style="background:#2f5f52"></i>anterior (interior, antihorario)</span>
        <span><i style="background:var(--gold)"></i>cierre cola &harr; cabeza</span>
      </div>

      <h2 style="margin-top:18px">Estado de los punteros</h2>
      <div class="pointers" id="pointerPanel"></div>
    </section>
  </div>

  <!-- ============== CONTROLS ============== -->
  <div class="grid" style="margin-top:18px">
    <section class="card">
      <h2>Agregar un modo a la lista</h2>
      <div class="inputs">
        <div><label>Nombre</label><input id="inName" placeholder="Ej: Drift" maxlength="18"></div>
        <div><label>Icono</label><input id="inIcon" value="🎚️" maxlength="4"></div>
        <div><label>Color</label><input id="inColor" type="color" value="#00e0d0"></div>
        <div><label>Potencia %</label><input id="inPower" type="number" min="0" max="100" value="80"></div>
        <div><label>Consumo %</label><input id="inConsumption" type="number" min="0" max="100" value="70"></div>
        <div><label>Posici&oacute;n</label>
          <select id="inWhere">
            <option value="end">Al final (nueva cola)</option>
            <option value="current">Despu&eacute;s del actual</option>
          </select>
        </div>
      </div>
      <div><label style="margin-top:12px">Descripci&oacute;n</label>
        <input id="inDescription" placeholder="Perfil definido por el conductor" maxlength="90"></div>
      <div class="row">
        <button class="action green" id="btnInsert">+ Insertar nodo</button>
      </div>
      <div class="notice" id="notice"></div>
    </section>

    <section class="card">
      <h2>Operaciones sobre la lista</h2>
      <div class="row" style="margin-top:0">
        <button class="action red" id="btnRemove">&#10005; Eliminar el modo actual</button>
        <button class="action gray" id="btnReset">&#10227; Reiniciar ECU</button>
      </div>
      <h2 style="margin-top:20px">Bit&aacute;cora de punteros</h2>
      <div class="log" id="eventLog"></div>
    </section>
  </div>
</div>

<script>
/* =======================================================================
   1. DRAWING HELPERS (ring geometry)
   ======================================================================= */
const CX = 160, CY = 160, R_OUTER = 148, R_NODE = 118, R_INNER = 92;

function point(radius, degrees){            // degrees -> x,y coordinate
  const a = degrees * Math.PI / 180;
  return [CX + radius * Math.cos(a), CY + radius * Math.sin(a)];
}
function arc(radius, from, to){             // SVG path of a clockwise arc
  const [x1,y1] = point(radius,from), [x2,y2] = point(radius,to);
  const delta = ((to - from) % 360 + 360) % 360;
  return `M ${x1} ${y1} A ${radius} ${radius} 0 ${delta>180?1:0} 1 ${x2} ${y2}`;
}
function arrow(radius, degrees, way, color){ // triangle tangent to the circle
  const [x,y] = point(radius, degrees);
  const spin = degrees + (way > 0 ? 90 : -90);
  return `<polygon points="-5,-4 -5,4 5,0" fill="${color}"
           transform="translate(${x},${y}) rotate(${spin})"/>`;
}

/* =======================================================================
   2. DRAW THE RING OF NODES
   ======================================================================= */
function drawRing(state){
  const svg = document.getElementById('ringSvg');
  if(state.empty){
    svg.innerHTML = '<text x="160" y="165" fill="#8ba0bd" text-anchor="middle" font-size="14">Lista vacia</text>';
    return;
  }

  const total = state.nodes.length;
  const step = 360 / total;
  const angle = i => -90 + i * step;           // the first node sits on top
  let parts = [];

  /* --- base circles: the track the pointers follow --- */
  parts.push(`<circle cx="${CX}" cy="${CY}" r="${R_OUTER}" fill="none" stroke="#3a4a63" stroke-width="2"/>`);
  parts.push(`<circle cx="${CX}" cy="${CY}" r="${R_INNER}" fill="none" stroke="#2f5f52" stroke-width="2" stroke-dasharray="5 6"/>`);

  /* --- tail -> head leg highlighted: this is where the circle CLOSES --- */
  if(total > 1){
    const tailIndex = state.nodes.findIndex(n => n.is_tail);
    const headIndex = state.nodes.findIndex(n => n.is_head);
    parts.push(`<path d="${arc(R_OUTER, angle(tailIndex), angle(headIndex))}" fill="none"
                   stroke="#ffc34d" stroke-width="4" stroke-linecap="round"/>`);
    parts.push(`<path d="${arc(R_INNER, angle(tailIndex), angle(headIndex))}" fill="none"
                   stroke="#ffc34d" stroke-width="3" stroke-dasharray="4 5"/>`);
  }

  /* --- direction arrows on every leg --- */
  for(let i = 0; i < total; i++){
    const middle = angle(i) + step / 2;
    const isClosing = state.nodes[i].is_tail && total > 1;
    parts.push(arrow(R_OUTER, middle,  1, isClosing ? '#ffc34d' : '#5a6f90'));   // next
    parts.push(arrow(R_INNER, middle, -1, isClosing ? '#ffc34d' : '#3f7f6d'));   // prev
  }

  /* --- the nodes themselves --- */
  state.nodes.forEach((item, i) => {
    const [x,y] = point(R_NODE, angle(i));
    const radius = item.is_current ? 25 : 19;
    const stroke = item.is_current ? item.color : '#2a3a52';
    parts.push(`<g class="node" data-name="${item.name}">
        ${item.is_current ? `<circle cx="${x}" cy="${y}" r="${radius+7}" fill="none" stroke="${item.color}" stroke-opacity=".35" stroke-width="2"/>` : ''}
        <circle cx="${x}" cy="${y}" r="${radius}" fill="#101925" stroke="${stroke}" stroke-width="${item.is_current?3:2}"/>
        <text x="${x}" y="${y+6}" text-anchor="middle" font-size="${item.is_current?20:15}">${item.icon}</text>
      </g>`);

    /* label with the name and its role (CABEZA / COLA) */
    const [lx,ly] = point(R_NODE + 44, angle(i));
    const anchor = Math.cos(angle(i)*Math.PI/180) > .2 ? 'start'
                 : Math.cos(angle(i)*Math.PI/180) < -.2 ? 'end' : 'middle';
    const role = item.is_head ? 'CABEZA' : (item.is_tail ? 'COLA' : '');
    parts.push(`<text x="${lx}" y="${ly}" text-anchor="${anchor}" font-size="12"
                   fill="${item.is_current ? item.color : '#8ba0bd'}" font-weight="${item.is_current?700:400}">${item.name}</text>`);
    if(role) parts.push(`<text x="${lx}" y="${ly+13}" text-anchor="${anchor}" font-size="9"
                   fill="#ffc34d" letter-spacing="1.5">${role}</text>`);
  });

  /* --- center text: a reminder that there is no end --- */
  parts.push(`<text x="${CX}" y="${CY-6}" text-anchor="middle" font-size="11" fill="#8ba0bd" letter-spacing="2">SIN FIN DE LISTA</text>`);
  parts.push(`<text x="${CX}" y="${CY+12}" text-anchor="middle" font-size="11" fill="#8ba0bd">${total} nodo(s) enlazados</text>`);

  svg.innerHTML = parts.join('');

  /* clicking a node means jumping straight to that mode */
  svg.querySelectorAll('.node').forEach(group => {
    group.onclick = () => send('/api/select', {name: group.dataset.name});
  });
}

/* =======================================================================
   3. RENDER THE WHOLE DASHBOARD FROM THE STATE PYTHON SENT
   ======================================================================= */
function render(state){
  document.getElementById('modeCount').textContent = state.size;

  if(state.empty){
    document.documentElement.style.setProperty('--accent', '#8ba0bd');
    document.getElementById('currentIcon').textContent = '⚠';
    document.getElementById('currentName').textContent = '—';
    document.getElementById('currentTag').textContent = 'lista vacia';
    document.getElementById('currentDesc').textContent = 'No hay modos en la ECU. Inserta uno nuevo o reinicia.';
    ['prevName','activeName','nextName','specSteering','specSuspension','specDrivetrain']
      .forEach(id => document.getElementById(id).textContent = '—');
    document.getElementById('powerArc').setAttribute('stroke-dasharray','0 999');
    document.getElementById('powerBar').style.width = '0%';
    document.getElementById('consumptionBar').style.width = '0%';
    document.getElementById('powerNum').textContent = '0%';
    document.getElementById('consumptionNum').textContent = '0%';
    document.getElementById('pointerPanel').innerHTML = '<div class="empty">cabeza = cola = actual = None</div>';
    drawRing(state); renderLog(state); return;
  }

  const mode = state.current;
  document.documentElement.style.setProperty('--accent', mode.color);
  document.getElementById('currentIcon').textContent = mode.icon;
  document.getElementById('currentName').textContent = mode.name;
  document.getElementById('currentTag').textContent = 'modo activo';
  document.getElementById('currentDesc').textContent = mode.description;

  document.getElementById('prevName').textContent   = state.prev;
  document.getElementById('activeName').textContent = mode.name;
  document.getElementById('nextName').textContent   = state.next;

  /* power arc: the circumference of r=112 is 2*pi*112 */
  const circumference = 2 * Math.PI * 112;
  document.getElementById('powerArc')
          .setAttribute('stroke-dasharray', `${circumference * mode.power / 100} ${circumference}`);

  document.getElementById('powerBar').style.width = mode.power + '%';
  document.getElementById('powerBar').style.background = mode.color;
  document.getElementById('consumptionBar').style.width = mode.consumption + '%';
  document.getElementById('consumptionBar').style.background = mode.consumption > 70 ? '#ff6b7a' : '#39d98a';
  document.getElementById('powerNum').textContent = mode.power + '%';
  document.getElementById('consumptionNum').textContent = mode.consumption + '%';

  document.getElementById('specSteering').textContent   = mode.steering;
  document.getElementById('specSuspension').textContent = mode.suspension;
  document.getElementById('specDrivetrain').textContent = mode.drivetrain;

  /* raw pointer panel, so the real structure stays visible */
  document.getElementById('pointerPanel').innerHTML = `
    <div>cabeza &rarr; <b>${state.head}</b> &nbsp;|&nbsp; cola &rarr; <b>${state.tail}</b> &nbsp;|&nbsp; tamanio = ${state.size}</div>
    <div>actual.anterior  &rarr; ${state.prev}</div>
    <div>actual           &rarr; ${mode.name}</div>
    <div>actual.siguiente &rarr; ${state.next}</div>
    <div class="closing">cola(${state.tail}).siguiente &rarr; cabeza(${state.head})</div>
    <div class="closing">cabeza(${state.head}).anterior &rarr; cola(${state.tail})</div>
    <div style="border-left-color:#2f5f52;white-space:normal">${state.diagram}</div>`;

  drawRing(state);
  renderLog(state);
}

function renderLog(state){
  const box = document.getElementById('eventLog');
  box.innerHTML = (state.log && state.log.length)
    ? state.log.map(line => `<p>${line}</p>`).join('')
    : '<p>Sin operaciones todavia. Usa las levas del volante.</p>';
}

/* =======================================================================
   4. TALKING TO THE BACKEND
   ======================================================================= */
async function send(route, body){
  const notice = document.getElementById('notice');
  notice.textContent = '';
  try{
    const reply = await fetch(route, {
      method: body === undefined ? 'GET' : 'POST',
      headers: {'Content-Type':'application/json'},
      body: body === undefined ? undefined : JSON.stringify(body)
    });
    const state = await reply.json();
    if(!reply.ok){ notice.textContent = state.error || 'Operacion rechazada'; return; }
    render(state);
  }catch(err){
    notice.textContent = 'No se pudo contactar la ECU: ' + err.message;
  }
}

/* =======================================================================
   5. WIRING THE BUTTONS
   ======================================================================= */
document.getElementById('btnNext').onclick   = () => send('/api/next', {});
document.getElementById('btnPrev').onclick   = () => send('/api/previous', {});
document.getElementById('btnRemove').onclick = () => send('/api/remove', {});
document.getElementById('btnReset').onclick  = () => send('/api/reset', {});

document.getElementById('btnInsert').onclick = () => {
  send('/api/insert', {
    name: document.getElementById('inName').value,
    icon: document.getElementById('inIcon').value,
    color: document.getElementById('inColor').value,
    description: document.getElementById('inDescription').value,
    power: Number(document.getElementById('inPower').value),
    consumption: Number(document.getElementById('inConsumption').value),
    after_current: document.getElementById('inWhere').value === 'current'
  });
  document.getElementById('inName').value = '';
  document.getElementById('inDescription').value = '';
};

/* the steering wheel paddles also answer to the keyboard */
document.addEventListener('keydown', event => {
  if(event.target.tagName === 'INPUT' || event.target.tagName === 'SELECT') return;
  if(event.key === 'ArrowRight') send('/api/next', {});
  if(event.key === 'ArrowLeft')  send('/api/previous', {});
});

/* startup: ask Python for the initial state */
send('/api/state');
</script>
</body>
</html>
"""


# ==============================================================================
# BLOCK 7 - ENTRY POINT: console demo and web server startup
# ==============================================================================
def console_demo() -> None:
    """Exercise the structure without any GUI, to watch it work as plain text.

    The printed text is Spanish: the console is also something the user reads.
    """
    print("=" * 72)
    print(" DEMOSTRACION DE LA LISTA CIRCULAR DOBLEMENTE ENLAZADA")
    print("=" * 72)
    print(" Lista inicial :", ECU)
    print(" Actual        :", ECU.show_current())
    print(" Cabeza / Cola :", ECU.head.data.name, "/", ECU.tail.data.name)

    print("\n Avanzando 4 veces con move_next():")
    for _ in range(4):
        print("   ->", ECU.move_next().name)
    print("   (se paso de Individual a Eco sin un solo 'if': eso es la circularidad)")

    print("\n Retrocediendo 2 veces con move_previous():")
    for _ in range(2):
        print("   <-", ECU.move_previous().name)

    print("\n Insertando 'Drift' despues del actual y eliminando 'Off-Road':")
    ECU.insert(DrivingMode(name="Drift", icon="💨", color="#ff8a3d",
                           description="Par total al eje trasero.",
                           power=98, consumption=95),
               after_current=True)
    ECU.remove("Off-Road")
    print("  ", ECU)
    print("   Cabeza:", ECU.head.data.name, "| Cola:", ECU.tail.data.name,
          "| Tamanio:", len(ECU))
    print("   Comprobacion del cierre del circulo:")
    print("     cola.siguiente  ==", ECU.tail.next.data.name,
          "(deberia ser la cabeza)")
    print("     cabeza.anterior ==", ECU.head.prev.data.name,
          "(deberia ser la cola)")

    print("\n Nombres via get_all():", [mode.name for mode in ECU.get_all()])
    print("=" * 72)


if __name__ == "__main__":
    import webbrowser

    console_demo()

    # Rebuild the list so the dashboard starts from the factory configuration.
    ECU = create_initial_list()
    EVENT_LOG.clear()

    print("\n Tablero disponible en:  http://127.0.0.1:5000")
    print(" Para detener el servidor pulsa Ctrl + C\n")
    try:
        webbrowser.open("http://127.0.0.1:5000")
    except Exception:
        pass
    app.run(host="127.0.0.1", port=5000, debug=False)
