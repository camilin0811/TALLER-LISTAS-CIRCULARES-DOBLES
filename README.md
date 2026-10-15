# TALLER: LISTAS CIRCULARES DOBLEMENTE ENLAZADAS

## Caso de estudio: Sistema de Infotenimiento y Modos de Conducción de un Vehículo Inteligente

Aplicación interactiva que simula la pantalla principal / volante de un automóvil.
El conductor navega **cíclicamente** entre los modos de conducción (Eco, Confort,
Sport, Off-Road, Individual) usando una **Lista Circular Doblemente Enlazada**
implementada desde cero, sin usar listas nativas de Python como estructura principal.

---

## Convención de idioma

- **El código está en inglés:** clases, métodos, atributos, variables, comentarios,
  docstrings, selectores CSS, identificadores del DOM y claves de la API REST.
- **La interfaz está en español:** todo texto que el conductor lee en pantalla
  (títulos, etiquetas, botones, descripciones de los modos, mensajes de error,
  bitácora y la demostración por consola).

---

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `vehicle_dashboard.py` | Proyecto completo: estructura de datos, backend Flask y tablero HTML/CSS/JS |
| `tests.py` | Banco de pruebas de la estructura y de la API (no necesita navegador) |
| `requirements.txt` | Única dependencia: Flask |

Todo el proyecto está en un solo script, organizado en siete bloques:

1. `DrivingMode` — el dato que viaja dentro de cada nodo
2. `Node` — la celda con los punteros `prev` y `next`
3. `CircularDoublyLinkedList` — la estructura de datos construida a mano
4. Datos de fábrica — los 5 modos que trae el vehículo
5. Backend Flask — API REST que expone la lista
6. Frontend — el tablero digital del automóvil
7. Punto de entrada — demostración por consola + servidor web

---

## Cómo ejecutarlo

### Requisitos
- Python 3.9 o superior
- Flask

### Pasos

1. Clonar o descargar el repositorio:
   ```
   git clone https://github.com/camilin0811/TALLER-LISTAS-CIRCULARES-DOBLES.git
   ```

2. Entrar a la carpeta:
   ```
   cd TALLER-LISTAS-CIRCULARES-DOBLES
   ```

3. Instalar la dependencia:
   ```
   pip install -r requirements.txt
   ```

4. Ejecutar el proyecto:
   ```
   python vehicle_dashboard.py
   ```

5. La consola muestra primero una demostración de la estructura y luego:
   ```
   Tablero disponible en:  http://127.0.0.1:5000
   ```
   El navegador se abre automáticamente. Si no lo hace, abre esa dirección a mano.

6. Para detener el servidor: `Ctrl + C`.

### Ejecutar solo las pruebas (sin servidor ni navegador)
```
python tests.py
```

---

## Qué permite hacer la interfaz

- Ver el **modo actual** destacado en el centro, con su gauge de potencia, su color
  propio, su descripción y su ficha técnica (dirección, suspensión, tracción).
- **Siguiente (▶)** y **Anterior (◀)** para recorrer la lista circular; también
  funcionan las flechas ← y → del teclado.
- **Agregar** un modo nuevo (nombre, icono, color, potencia, consumo) al final de la
  lista o justo después del modo actual.
- **Eliminar** el modo actual y **reiniciar** la ECU a los 5 modos de fábrica.
- Clic sobre cualquier nodo del anillo para saltar directamente a ese modo.
- **Anillo de punteros** que muestra la naturaleza circular de la estructura:
  - anillo exterior con flechas horarias = punteros `next`
  - anillo interior punteado con flechas antihorarias = punteros `prev`
  - tramo **dorado** que resalta el cierre `tail ↔ head`
  - etiquetas `CABEZA` y `COLA` sobre los nodos correspondientes
- **Panel de punteros** en texto crudo y **bitácora** con las últimas 12 operaciones.

---

## Métodos implementados

| Método | Equivalente del enunciado | Costo | Qué hace |
|---|---|---|---|
| `insert(data, after_current)` | `insertar` | O(1) | Agrega un nodo al final o detrás del actual |
| `remove(name=None)` | `eliminar` | O(1) + búsqueda | Quita el nodo actual o uno por nombre |
| `move_next()` | `avanzar_siguiente` | O(1) | `current = current.next` |
| `move_previous()` | `retroceder_anterior` | O(1) | `current = current.prev` |
| `show_current()` | `mostrar_actual` | O(1) | Texto del modo activo con sus dos vecinos |
| `get_all()` | `obtener_todos` | O(n) | Copia de salida con todos los datos |
| `find(name)` | `buscar` | O(n) | Devuelve el nodo con ese nombre |
| `select(name)` | `seleccionar` | O(n) | Salto directo a un modo |
| `is_empty()` / `__len__()` | `esta_vacia` / `len` | O(1) | Consultas de control |
| `snapshot()` | `estado` | O(n) | Fotografía en JSON para el frontend |

Atributos de control de la lista: `head` (cabeza), `tail` (cola), `current` (el nodo
que ve el conductor) y `size` (tamaño).

---

## Por qué una Lista Circular Doblemente Enlazada en la industria automotriz

El conductor solo dispone de dos estímulos físicos: una leva que dice **siguiente** y
otra que dice **anterior** (o un dial que gira en los dos sentidos). No puede escribir
un índice ni elegir una posición. Esa interfaz exige exactamente tres propiedades:

1. **Circular.** El conductor nunca debe encontrar un *fin de lista*. Si está en
   Individual (el último modo) y vuelve a pulsar la leva derecha, debe aparecer Eco.
   En una lista normal habría que preguntar en cada pulsación "¿ya llegué al final?,
   entonces reinicio al principio". Aquí el último nodo apunta al primero, así que ese
   caso especial **desaparece**: el recorrido es infinito sin un solo `if`.

2. **Doblemente enlazada.** La leva izquierda tiene que retroceder un modo. Con
   punteros solo hacia adelante habría que recorrer toda la lista para encontrar al
   vecino de atrás: O(n) y, en un volante, un retardo visible. Con el puntero `prev`,
   retroceder cuesta O(1), igual que avanzar. Simetría de costo = simetría de la
   experiencia del conductor.

3. **Inserción y eliminación baratas.** Un usuario agrega el perfil "Individual 2", el
   taller desactiva Off-Road en un auto sin tracción total, o una emisora de radio se
   guarda o se borra. En una lista enlazada eso es reconectar cuatro punteros, O(1),
   sin desplazar el resto de los elementos como ocurriría en un arreglo.

Con lo anterior, cada pulsación del volante se resuelve en **tiempo constante** y con
una sola instrucción.

---

## Los punteros `prev` y `next` en los extremos de la lista

En una lista doblemente enlazada **normal** los extremos están abiertos:

```
None <- [Eco] <-> [Confort] <-> [Sport] -> None
         head                     tail
```

`head.prev = None` y `tail.next = None`. Consecuencia práctica: cada vez que el
conductor pulsa la leva hay que preguntar "¿me quedé sin lista?" y, si la respuesta es
sí, saltar manualmente al otro extremo.

En una lista **circular doble** esos dos `None` se reemplazan el uno por el otro:

```
        ┌─────────────────── tail.next ─────────────────┐
        ↓                                               │
     [Eco] <-> [Confort] <-> [Sport] <-> [Off-Road] <-> [Individual]
        │                                               ↑
        └─────────────────── head.prev ─────────────────┘
```

Las dos igualdades que definen la estructura son:

- **`tail.next = head`** → desde el último modo, avanzar lleva al primero.
- **`head.prev = tail`** → desde el primer modo, retroceder lleva al último.

Caso límite importante: **si la lista tiene un solo nodo, ese nodo es su propio `next`
y su propio `prev`**. Nunca hay un `None` dentro de una lista circular ya construida.

Por eso la navegación se reduce a una sola línea, sin ningún `if` de final de lista:

```python
self.current = self.current.next   # leva derecha
self.current = self.current.prev   # leva izquierda
```

Y hay una consecuencia sobre los recorridos: la condición de parada **no** puede ser
`while node is not None`, porque en una lista circular eso nunca termina. La condición
correcta es "volví a la cabeza":

```python
node = self.head
while True:
    items.append(node.data)
    node = node.next
    if node is self.head:     # dimos la vuelta completa
        break
```

---

## API REST del backend

| Ruta | Método | Operación sobre la lista |
|---|---|---|
| `/` | GET | Entrega el tablero HTML |
| `/api/state` | GET | Fotografía completa de la lista |
| `/api/next` | POST | `move_next()` |
| `/api/previous` | POST | `move_previous()` |
| `/api/select` | POST | `select(name)` |
| `/api/insert` | POST | `insert(mode, after_current)` |
| `/api/remove` | POST | `remove(name)` |
| `/api/reset` | POST | Recrea la lista con los modos de fábrica |

Cada ruta devuelve el estado real de los punteros después de la operación, por lo que
la interfaz nunca dibuja suposiciones: pinta lo que la estructura de datos reporta.

Claves del JSON que viaja al navegador: `empty`, `size`, `head`, `tail`, `current`,
`prev`, `next`, `nodes`, `text`, `diagram` y `log`. Cada nodo de `nodes` incluye
además `is_head`, `is_tail` e `is_current`.

---

## Casos de borde cubiertos por `tests.py`

- Lista vacía: navegar, eliminar y mostrar no provocan errores
- Lista de un solo nodo: se apunta a sí mismo en ambos sentidos
- Eliminar la cabeza, eliminar la cola y eliminar el nodo que se está viendo
- Insertar en lista vacía (`head` = `tail` = `current`)
- Insertar justo detrás de la cola (la cola se desplaza)
- Vuelta completa en los dos sentidos
- Rechazo de nombres duplicados y de nombres vacíos
- Vaciar la lista por completo desde la API y volver a poblarla
