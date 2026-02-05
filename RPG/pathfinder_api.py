"""
Pathfinder RPG - FastAPI Backend
Servidor REST API con SQLite
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3
import base64
import os

app = FastAPI(title="Pathfinder RPG API", version="1.0.0")

# Ruta al archivo HTML
HTML_FILE = os.path.join(os.path.dirname(__file__), "pathfinder_web_fastapi.html")

@app.get("/", response_class=FileResponse)
async def serve_frontend():
    """Sirve el frontend HTML"""
    return FileResponse(HTML_FILE, media_type="text/html")

# CORS para permitir conexiones desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE = "pathfinder_fastapi.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializar la base de datos con las tablas necesarias"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabla de personajes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            clase TEXT DEFAULT 'Guerrero',
            raza TEXT DEFAULT 'Humano',
            nivel INTEGER DEFAULT 1,
            hp_max INTEGER DEFAULT 10,
            hp_actual INTEGER DEFAULT 10,
            oro INTEGER DEFAULT 0,
            fuerza INTEGER DEFAULT 10,
            destreza INTEGER DEFAULT 10,
            constitucion INTEGER DEFAULT 10,
            inteligencia INTEGER DEFAULT 10,
            sabiduria INTEGER DEFAULT 10,
            carisma INTEGER DEFAULT 10,
            notas TEXT DEFAULT ''
        )
    ''')
    
    # Tabla de inventario
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personaje_id INTEGER,
            item TEXT NOT NULL,
            cantidad INTEGER DEFAULT 1,
            peso REAL DEFAULT 0,
            descripcion TEXT,
            valor INTEGER DEFAULT 0,
            imagen TEXT,
            FOREIGN KEY (personaje_id) REFERENCES personajes(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabla de habilidades del personaje
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habilidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personaje_id INTEGER,
            nombre TEXT NOT NULL,
            atributo TEXT DEFAULT 'inteligencia',
            rango INTEGER DEFAULT 1,
            entrenamiento TEXT DEFAULT 'Básico',
            FOREIGN KEY (personaje_id) REFERENCES personajes(id) ON DELETE CASCADE
        )
    ''')
    
    # Biblioteca de objetos predefinidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS objetos_predefinidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT DEFAULT 'Misc',
            peso REAL DEFAULT 0,
            valor INTEGER DEFAULT 0,
            descripcion TEXT,
            imagen TEXT
        )
    ''')
    
    # Biblioteca de habilidades predefinidas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habilidades_predefinidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            clase TEXT,
            nivel_minimo INTEGER DEFAULT 1,
            entrenamiento TEXT DEFAULT 'Básico',
            atributo TEXT DEFAULT 'inteligencia'
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada")


# ==================== MODELOS ====================

class PersonajeCreate(BaseModel):
    nombre: str
    clase: Optional[str] = "Guerrero"
    raza: Optional[str] = "Humano"
    nivel: Optional[int] = 1
    hp_max: Optional[int] = 10
    hp_actual: Optional[int] = 10
    oro: Optional[int] = 0
    fuerza: Optional[int] = 10
    destreza: Optional[int] = 10
    constitucion: Optional[int] = 10
    inteligencia: Optional[int] = 10
    sabiduria: Optional[int] = 10
    carisma: Optional[int] = 10
    notas: Optional[str] = ""


class PersonajeUpdate(BaseModel):
    nombre: Optional[str] = None
    clase: Optional[str] = None
    raza: Optional[str] = None
    nivel: Optional[int] = None
    hp_max: Optional[int] = None
    hp_actual: Optional[int] = None
    oro: Optional[int] = None
    fuerza: Optional[int] = None
    destreza: Optional[int] = None
    constitucion: Optional[int] = None
    inteligencia: Optional[int] = None
    sabiduria: Optional[int] = None
    carisma: Optional[int] = None
    notas: Optional[str] = None


class InventarioCreate(BaseModel):
    personaje_id: int
    item: str
    cantidad: Optional[int] = 1
    peso: Optional[float] = 0
    descripcion: Optional[str] = ""
    valor: Optional[int] = 0
    imagen: Optional[str] = None


class InventarioUpdate(BaseModel):
    cantidad: Optional[int] = None


class HabilidadCreate(BaseModel):
    personaje_id: int
    nombre: str
    atributo: Optional[str] = "inteligencia"
    rango: Optional[int] = 1
    entrenamiento: Optional[str] = "Básico"


class ObjetoCreate(BaseModel):
    nombre: str
    tipo: Optional[str] = "Misc"
    peso: Optional[float] = 0
    valor: Optional[int] = 0
    descripcion: Optional[str] = ""
    imagen: Optional[str] = None


class HabilidadLibCreate(BaseModel):
    nombre: str
    clase: Optional[str] = None
    nivel_minimo: Optional[int] = 1
    entrenamiento: Optional[str] = "Básico"
    atributo: Optional[str] = "inteligencia"


# ==================== ENDPOINTS PERSONAJES ====================

@app.get("/api/personajes")
def get_personajes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personajes ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/api/personajes/{id}")
def get_personaje(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personajes WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return dict(row)


@app.post("/api/personajes")
def create_personaje(personaje: PersonajeCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO personajes (nombre, clase, raza, nivel, hp_max, hp_actual, oro,
                               fuerza, destreza, constitucion, inteligencia, sabiduria, carisma, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (personaje.nombre, personaje.clase, personaje.raza, personaje.nivel,
          personaje.hp_max, personaje.hp_actual, personaje.oro,
          personaje.fuerza, personaje.destreza, personaje.constitucion,
          personaje.inteligencia, personaje.sabiduria, personaje.carisma, personaje.notas))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "message": "Personaje creado"}


@app.put("/api/personajes/{id}")
def update_personaje(id: int, personaje: PersonajeUpdate):
    conn = get_db()
    cursor = conn.cursor()
    
    # Obtener datos actuales
    cursor.execute("SELECT * FROM personajes WHERE id = ?", (id,))
    current = cursor.fetchone()
    if not current:
        conn.close()
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    current = dict(current)
    updates = personaje.dict(exclude_unset=True)
    
    for key, value in updates.items():
        if value is not None:
            current[key] = value
    
    cursor.execute('''
        UPDATE personajes SET nombre=?, clase=?, raza=?, nivel=?, hp_max=?, hp_actual=?, oro=?,
                             fuerza=?, destreza=?, constitucion=?, inteligencia=?, sabiduria=?, carisma=?, notas=?
        WHERE id=?
    ''', (current['nombre'], current['clase'], current['raza'], current['nivel'],
          current['hp_max'], current['hp_actual'], current['oro'],
          current['fuerza'], current['destreza'], current['constitucion'],
          current['inteligencia'], current['sabiduria'], current['carisma'], current['notas'], id))
    conn.commit()
    conn.close()
    return {"message": "Personaje actualizado"}


@app.delete("/api/personajes/{id}")
def delete_personaje(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventario WHERE personaje_id = ?", (id,))
    cursor.execute("DELETE FROM habilidades WHERE personaje_id = ?", (id,))
    cursor.execute("DELETE FROM personajes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"message": "Personaje eliminado"}


# ==================== ENDPOINTS INVENTARIO ====================

@app.get("/api/inventario/{personaje_id}")
def get_inventario(personaje_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventario WHERE personaje_id = ?", (personaje_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/api/inventario")
def create_inventario(item: InventarioCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inventario (personaje_id, item, cantidad, peso, descripcion, valor, imagen)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (item.personaje_id, item.item, item.cantidad, item.peso, item.descripcion, item.valor, item.imagen))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "message": "Item agregado al inventario"}


@app.put("/api/inventario/{id}")
def update_inventario(id: int, item: InventarioUpdate):
    conn = get_db()
    cursor = conn.cursor()
    if item.cantidad is not None:
        cursor.execute("UPDATE inventario SET cantidad = ? WHERE id = ?", (item.cantidad, id))
    conn.commit()
    conn.close()
    return {"message": "Inventario actualizado"}


@app.delete("/api/inventario/{id}")
def delete_inventario(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventario WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"message": "Item eliminado del inventario"}


# ==================== ENDPOINTS HABILIDADES ====================

@app.get("/api/habilidades/{personaje_id}")
def get_habilidades(personaje_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habilidades WHERE personaje_id = ?", (personaje_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/api/habilidades")
def create_habilidad(habilidad: HabilidadCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO habilidades (personaje_id, nombre, atributo, rango, entrenamiento)
        VALUES (?, ?, ?, ?, ?)
    ''', (habilidad.personaje_id, habilidad.nombre, habilidad.atributo, habilidad.rango, habilidad.entrenamiento))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "message": "Habilidad agregada"}


@app.delete("/api/habilidades/{id}")
def delete_habilidad(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habilidades WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"message": "Habilidad eliminada"}


# ==================== ENDPOINTS BIBLIOTECA OBJETOS ====================

@app.get("/api/objetos")
def get_objetos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM objetos_predefinidos ORDER BY nombre")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/api/objetos")
def create_objeto(objeto: ObjetoCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO objetos_predefinidos (nombre, tipo, peso, valor, descripcion, imagen)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (objeto.nombre, objeto.tipo, objeto.peso, objeto.valor, objeto.descripcion, objeto.imagen))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "message": "Objeto creado"}


@app.delete("/api/objetos/{id}")
def delete_objeto(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM objetos_predefinidos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"message": "Objeto eliminado"}


# ==================== ENDPOINTS BIBLIOTECA HABILIDADES ====================

@app.get("/api/habilidades-lib")
def get_habilidades_lib():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habilidades_predefinidas ORDER BY nombre")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/api/habilidades-lib")
def create_habilidad_lib(habilidad: HabilidadLibCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO habilidades_predefinidas (nombre, clase, nivel_minimo, entrenamiento, atributo)
        VALUES (?, ?, ?, ?, ?)
    ''', (habilidad.nombre, habilidad.clase, habilidad.nivel_minimo, habilidad.entrenamiento, habilidad.atributo))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "message": "Habilidad creada"}


@app.delete("/api/habilidades-lib/{id}")
def delete_habilidad_lib(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habilidades_predefinidas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"message": "Habilidad eliminada"}


# ==================== HEALTH CHECK ====================

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "FastAPI Pathfinder Server Running"}


# Inicializar DB al arrancar
init_db()

if __name__ == "__main__":
    import uvicorn
    print("🎮 Iniciando Pathfinder RPG FastAPI Server...")
    print("📍 API disponible en: http://localhost:8000")
    print("📚 Documentación: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
