from flask import Flask, jsonify, send_file
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Necesario para generar gráficas en servidores sin interfaz gráfica
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# --- 1. BASE DE DATOS (BD) ---
def init_db():
    conn = sqlite3.connect('videojuegos.db')
    cursor = conn.cursor()
    
    # Crear tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videojuegos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            plataforma TEXT NOT NULL,
            genero TEXT NOT NULL,
            ventas_millones REAL NOT NULL
        )
    ''')
    
    # Datos de prueba sobre videojuegos
    cursor.execute('SELECT COUNT(*) FROM videojuegos')
    if cursor.fetchone()[0] == 0:
        juegos = [
            ('The Legend of Zelda: TOTK', 'Nintendo Switch', 'Aventura', 20.5),
            ('God of War Ragnarök', 'PlayStation 5', 'Acción', 15.2),
            ('Elden Ring', 'Multiplataforma', 'RPG', 23.0),
            ('Red Dead Redemption 2', 'Multiplataforma', 'Mundo Abierto', 60.0),
            ('Mario Kart 8 Deluxe', 'Nintendo Switch', 'Carreras', 62.0),
            ('Halo Infinite', 'Xbox / PC', 'Shooter', 10.0)
        ]
        cursor.executemany(
            'INSERT INTO videojuegos (titulo, plataforma, genero, ventas_millones) VALUES (?, ?, ?, ?)',
            juegos
        )
        conn.commit()
    conn.close()

init_db()

# --- 2. RUTA PRINCIPAL (HTML CON NAVEGACIÓN) ---
@app.route("/")
def inicio():
    return """
    <h1>Servidor de Analítica de Videojuegos</h1>
    <p>Selecciona una opción:</p>
    <ul>
        <li><a href="/videojuegos">Ver datos JSON de la Base de Datos</a></li>
        <li><a href="/grafica">Ver Gráfica Analítica (Jupyter/Matplotlib)</a></li>
    </ul>
    """

# --- 3. RUTA DE DATOS (BD Y DATAFRAME) ---
@app.route("/videojuegos")
def obtener_videojuegos():
    conn = sqlite3.connect('videojuegos.db')
    # Leer de la BD directamente a un DataFrame de Pandas
    df = pd.read_sql_query("SELECT * FROM videojuegos", conn)
    conn.close()
    
    return jsonify({
        "status": "exito",
        "origen": "Base de Datos SQLite + Pandas DataFrame",
        "total_registros": len(df),
        "datos": df.to_dict(orient='records')
    })

# --- 4. RUTA DE GRAFICA (ANALÍTICA VISUAL COMO EL PIZARRÓN) ---
@app.route("/grafica")
def generar_grafica():
    conn = sqlite3.connect('videojuegos.db')
    df = pd.read_sql_query("SELECT genero, SUM(ventas_millones) as total_ventas FROM videojuegos GROUP BY genero", conn)
    conn.close()
    
    # Crear la gráfica con Matplotlib (igual a la del pizarrón)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(df['total_ventas'], labels=df['genero'], autopct='%1.1f%%', startangle=90)
    ax.set_title('Distribución de Ventas por Género de Videojuego')
    
    # Guardar gráfica en memoria para enviarla a la web
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
