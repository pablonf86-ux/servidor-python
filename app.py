from flask import Flask, jsonify, render_template_string
import sqlite3
import pandas as pd

app = Flask(__name__)

# --- 1. BASE DE DATOS SQLITE ---
def init_db():
    conn = sqlite3.connect('videojuegos.db')
    cursor = conn.cursor()
    
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

# --- 2. PLANTILLA HTML ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analítica de Videojuegos</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 15px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #38bdf8;
            font-size: 22px;
        }
        .card {
            background-color: #1e293b;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 13px;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }
        th {
            background-color: #334155;
            color: #38bdf8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Analítica & Base de Datos de Videojuegos</h1>

        <div class="card">
            <h2>Ventas Totales por Género (Gráfica de Barras)</h2>
            <div class="chart-container">
                <canvas id="barChart"></canvas>
            </div>
        </div>

        <div class="card">
            <h2>Registros de la Base de Datos</h2>
            <div style="overflow-x: auto;">
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
                            <td>#{{ juego.id }}</td>
                            <td><strong>{{ juego.titulo }}</strong></td>
                            <td>{{ juego.plataforma }}</td>
                            <td>{{ juego.genero }}</td>
                            <td>{{ juego.anio_lanzamiento }}</td>
                            <td><strong>{{ juego.ventas_millones }} M</strong></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('barChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: {{ generos | tojson }},
                datasets: [{
                    label: 'Ventas en Millones',
                    data: {{ ventas | tojson }},
                    backgroundColor: '#38bdf8',
                    borderColor: '#0284c7',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#f8fafc' },
                        grid: { color: '#334155' }
                    },
                    x: {
                        ticks: { color: '#f8fafc' },
                        grid: { color: '#334155' }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#f8fafc' }
                    }
                }
            }
        });
    </script>
</body>
</html>"""

# --- 3. RUTAS FLASK ---
@app.route("/")
def dashboard():
    conn = sqlite3.connect('videojuegos.db')
    df_juegos = pd.read_sql_query("SELECT * FROM videojuegos ORDER BY ventas_millones DESC", conn)
    juegos = df_juegos.to_dict(orient='records')
    
    df_grafica = pd.read_sql_query("SELECT genero, SUM(ventas_millones) as total_ventas FROM videojuegos GROUP BY genero ORDER BY total_ventas DESC", conn)
    generos = df_grafica['genero'].tolist()
    ventas = df_grafica['total_ventas'].tolist()
    conn.close()
    
    return render_template_string(HTML_TEMPLATE, juegos=juegos, generos=generos, ventas=ventas)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
