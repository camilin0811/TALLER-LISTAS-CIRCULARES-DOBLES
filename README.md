# TALLER: LISTAS CIRCULARES DOBLEMENTE ENLAZADAS

## Caso de estudio: Sistema de Infotenimiento y Modos de Conducción de un Vehículo Inteligente

Aplicación interactiva que simula la pantalla principal / volante de un automóvil.
El conductor navega **cíclicamente** entre los modos de conducción (Eco, Confort,
Sport, Off-Road, Individual) usando una **Lista Circular Doblemente Enlazada**
implementada desde cero, sin usar listas nativas de Python como estructura principal.

---

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `dashboard_vehiculo.py` | Proyecto completo: estructura de datos, backend Flask y tablero HTML/CSS/JS |
| `pruebas.py` | Banco de pruebas de la estructura y de la API (no necesita navegador) |
| `requirements.txt` | Única dependencia: Flask |

Todo el proyecto está en un solo script, organizado en siete bloques:

1. `ModoConduccion` — el dato que viaja dentro de cada nodo
2. `Nodo` — la celda con los punteros `anterior` y `siguiente`
3. `ListaCircularDoble` — la estructura de datos construida a mano
4. Datos de fábrica — los 5 modos que trae el vehículo
5. Backend Flask — API REST que expone la lista
6. Frontend — el tablero digital del automóvil
7. Arranque — demostración por consola + servidor web

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
   python dashboard_vehiculo.py
   ```

5. La consola muestra primero una demostración de la estructura y luego:
   ```
   Tablero disponible en:  http://127.0.0.1:5000
   ```
   El navegador se abre automáticamente. Si no lo hace, abre esa dirección a mano.

6. Para detener el servidor: `Ctrl + C`.

### Ejecutar solo las pruebas (sin servidor ni navegador)
```
python pruebas.py
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
  - anillo exterior con flechas horarias = punteros `siguiente`
  - anillo interior punteado con flechas antihorarias = punteros `anterior`
  - tramo **dorado** que resalta el cierre `cola ↔ cabeza`
  - etiquetas `CABEZA` y `COLA` sobre los nodos correspondientes
- **Panel de punteros** en texto crudo y **bitácora** con las últimas 12 operaciones.

---

## Métodos implementados

| Método | Costo | Qué hace |
|---|---|---|
| `insertar(dato, despues_del_actual)` | O(1) | Agrega un nodo al final o detrás del actual |
| `eliminar(nombre=None)` | O(1) / O(n) con búsqueda | Quita el nodo actual o uno por nombre |
| `avanzar_siguiente()` | O(1) | `actual = actual.siguiente` |
| `retroceder_anterior()` | O(1) | `actual = actual.anterior` |
| `mostrar_actual()` | O(1) | Texto del modo activo con sus dos vecinos |
| `obtener_todos()` | O(n) | Copia de salida con todos los datos |
| `buscar(nombre)` | O(n) | Devuelve el nodo con ese nombre |
| `seleccionar(nombre)` | O(n) | Salto directo a un modo |
| `esta_vacia()` / `__len__()` | O(1) | Consultas de control |
| `estado()` | O(n) | Fotografía en JSON para el frontend |

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
   vecino de atrás: O(n) y, en un volante, un retardo visible. Con el puntero
   `anterior`, retroceder cuesta O(1), igual que avanzar. Simetría de costo = simetría
   de la experiencia del conductor.

3. **Inserción y eliminación baratas.** Un usuario agrega el perfil "Individual 2", el
   taller desactiva Off-Road en un auto sin tracción total, o una emisora de radio se
   guarda o se borra. En una lista enlazada eso es reconectar cuatro punteros, O(1),
   sin desplazar el resto de los elementos como ocurriría en un arreglo.

Con lo anterior, cada pulsación del volante se resuelve en **tiempo constante** y con
una sola instrucción.

---

## Los punteros `anterior` y `siguiente` en los extremos de la lista

En una lista doblemente enlazada **normal** los extremos están abiertos:

```
None <- [Eco] <-> [Confort] <-> [Sport] -> None
         cabeza                    cola
```

`cabeza.anterior = None` y `cola.siguiente = None`. Consecuencia práctica: cada vez
que el conductor pulsa la leva hay que preguntar "¿me quedé sin lista?" y, si la
respuesta es sí, saltar manualmente al otro extremo.

En una lista **circular doble** esos dos `None` se reemplazan el uno por el otro:

```
        ┌──────────────── cola.siguiente ───────────────┐
        ↓                                               │
     [Eco] <-> [Confort] <-> [Sport] <-> [Off-Road] <-> [Individual]
        │                                               ↑
        └──────────────── cabeza.anterior ──────────────┘
```

Las dos igualdades que definen la estructura son:

- **`cola.siguiente = cabeza`** → desde el último modo, avanzar lleva al primero.
- **`cabeza.anterior = cola`** → desde el primer modo, retroceder lleva al último.

Caso límite importante: **si la lista tiene un solo nodo, ese nodo es su propio
`siguiente` y su propio `anterior`**. Nunca hay un `None` dentro de una lista circular
ya construida.

Por eso la navegación se reduce a una sola línea, sin ningún `if` de final de lista:

```python
self.actual = self.actual.siguiente   # leva derecha
self.actual = self.actual.anterior    # leva izquierda
```

Y hay una consecuencia sobre los recorridos: la condición de parada **no** puede ser
`while nodo is not None`, porque en una lista circular eso nunca termina. La condición
correcta es "volví a la cabeza":

```python
nodo = self.cabeza
while True:
    elementos.append(nodo.dato)
    nodo = nodo.siguiente
    if nodo is self.cabeza:     # dimos la vuelta completa
        break
```

---

## API REST del backend

| Ruta | Método | Operación sobre la lista |
|---|---|---|
| `/` | GET | Entrega el tablero HTML |
| `/api/estado` | GET | Fotografía completa de la lista |
| `/api/siguiente` | POST | `avanzar_siguiente()` |
| `/api/anterior` | POST | `retroceder_anterior()` |
| `/api/seleccionar` | POST | `seleccionar(nombre)` |
| `/api/insertar` | POST | `insertar(modo, despues_del_actual)` |
| `/api/eliminar` | POST | `eliminar(nombre)` |
| `/api/reiniciar` | POST | Recrea la lista con los modos de fábrica |

Cada ruta devuelve el estado real de los punteros después de la operación, por lo que
la interfaz nunca dibuja suposiciones: pinta lo que la estructura de datos reporta.

---

## Casos de borde cubiertos por `pruebas.py`

- Lista vacía: navegar, eliminar y mostrar no provocan errores
- Lista de un solo nodo: se apunta a sí mismo en ambos sentidos
- Eliminar la cabeza, eliminar la cola y eliminar el nodo que se está viendo
- Insertar en lista vacía (cabeza = cola = actual)
- Insertar justo detrás de la cola (la cola se desplaza)
- Vuelta completa en los dos sentidos
- Rechazo de nombres duplicados y de nombres vacíos
- Vaciar la lista por completo desde la API y volver a poblarla
