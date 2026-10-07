from flask import Flask, jsonify, render_template_string
import sqlite3
import pandas as pd

app = Flask(__name__)

# --- 1. CREACIÓN Y POBLADO DE LA BASE DE DATOS (SQLITE) ---
def init_db():
    conn = sqlite3.connect('videojuegos.db')
    cursor = conn.cursor()
    
    # Crear tabla de la Base de Datos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videojuegos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            plataforma TEXT NOT NULL,
            genero TEXT NOT NULL,
            ventas_millones REAL NOT NULL,
            anio_lanzamiento INTEGER NOT NULL
        )
    ''')
    
    # Insertar datos de prueba relacionales si está vacía
    cursor.execute('SELECT COUNT(*) FROM videojuegos')
    if cursor.fetchone()[0] == 0:
        juegos = [
            ('The Legend of Zelda: TOTK', 'Nintendo Switch', 'Aventura', 20.5, 2023),
            ('God of War Ragnarök', 'PlayStation 5', 'Acción', 15.2, 2022),
            ('Elden Ring', 'Multiplataforma', 'RPG', 23.0, 2022),
            ('Red Dead Redemption 2', 'Multiplataforma', 'Mundo Abierto', 60.0, 2018),
            ('Mario Kart 8 Deluxe', 'Nintendo Switch', 'Carreras', 62.0, 2017),
            ('Halo Infinite', 'Xbox / PC', 'Shooter', 10.0, 2021),
            ('Minecraft', 'Multiplataforma', 'Construcción', 300.0, 2011),
            ('GTA V', 'Multiplataforma', 'Mundo Abierto', 190.0, 2013)
        ]
        cursor.executemany(
            'INSERT INTO videojuegos (titulo, plataforma, genero, ventas_millones, anio_lanzamiento) VALUES (?, ?, ?, ?, ?)',
            juegos
        )
        conn.commit()
    conn.close()

init_db()

# --- 2. PLANTILLA HTML CON GRÁFICA DE BARRAS Y TABLAS DE BD ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Base de Datos & Analítica de Videojuegos</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 15px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #38bdf8;
            margin-bottom: 5px;
            font-size: 22px;
        }
        p.subtitle {
            text-align: center;
            color: #94a3b8;
            margin-bottom: 20px;
            font-size: 13px;
        }
        .card {
            background-color: #1e293b;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
        }
        h2 {
            color: #f1f5f9;
            font-size: 16px;
            margin-top: 0;
            border-bottom: 2px solid #334155;
            padding-bottom: 8px;
        }
        .chart-container {
            position: relative;
            height: 320px;
            width: 100%;
        }
        .table-responsive {
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 13px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }
        th {
            background-color: #334155;
            color: #38bdf8;
        }
        tr:hover {
            background-color: #334155;
        }
        .badge {
            background-color: #0284c7;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 11px;
            white-space: nowrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Analítica de Datos & Base de Datos</h1>
        <p class="subtitle">Conexión SQLite + Pandas DataFrame + Gráfica de Barras</p>

        <!-- Gráfica de Barras -->
        <div class="card">
            <h2>📈 Gráfica de Barras: Ventas Totales por Género (Millones)</h2>
            <div class="chart-container">
                <canvas id="barChart"></canvas>
            </div>
        </div>

        <!-- Tabla de la Base de Datos -->
        <div class="card">
            <h2>🗄️ Tabla Relacional `videojuegos` (SQLite DB)</h2>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Título</th>
                            <th>Plataforma</th>
                            <th>Género</th>
                            <th>Año</th>
                            <th>Ventas (M)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for juego in juegos %}
                        <tr>
                            <td><code>#{{ juego.id }}</code></td>
                            <td><strong>{{ juego.titulo }}</strong></td>
                            <td><span class="badge">{{ juego.plataforma }}</span></td>
                            <td>{{ juego.genero }}</td>
                            <td>{{ juego.anio_lanzamiento }}</td>
                            <td><strong>{{ juego.ventas_millones }} M</strong></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
