from flask import Flask, jsonify, render_template_string
import sqlite3
import pandas as pd

app = Flask(__name__)

# --- 1. BASE DE DATOS SQLITE (TIENDA DE TECNOLOGÍA) ---
def init_db():
    conn = sqlite3.connect('tienda.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL,
            metodo_pago TEXT NOT NULL,
            monto_total REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM ventas')
    if cursor.fetchone()[0] == 0:
        datos_ejemplo = [
            ('Laptop Pro 15', 'Cómputo', 1200.00, 5, 'Tarjeta de Crédito', 6000.00, 18),
            ('Smartphone X', 'Telefonía', 800.00, 8, 'Transferencia', 6400.00, 25),
            ('Audífonos Noise-Cancel', 'Audio', 150.00, 15, 'Tarjeta de Crédito', 2250.00, 4),
            ('Monitor 4K 27"', 'Cómputo', 350.00, 10, 'Efectivo', 3500.00, 12),
            ('Teclado Mecánico', 'Accesorios', 90.00, 20, 'Transferencia', 1800.00, 30),
            ('Tablet Pro 11', 'Telefonía', 600.00, 6, 'Tarjeta de Crédito', 3600.00, 3),
            ('Cámara Web HD', 'Accesorios', 50.00, 12, 'Efectivo', 600.00, 15),
            ('Bocina Bluetooth', 'Audio', 80.00, 14, 'Transferencia', 1120.00, 8),
            ('Disco Duro NVMe 1TB', 'Cómputo', 110.00, 18, 'Tarjeta de Crédito', 1980.00, 2),
            ('Smartwatch Sport', 'Telefonía', 210.00, 9, 'Efectivo', 1890.00, 14)
        ]
        cursor.executemany(
            'INSERT INTO ventas (producto, categoria, precio, cantidad, metodo_pago, monto_total, stock) VALUES (?, ?, ?, ?, ?, ?, ?)',
            datos_ejemplo
        )
        conn.commit()
    conn.close()

init_db()

# --- 2. PLANTILLA HTML DASHBOARD COMPLETO ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Base de Datos - Tienda de Tecnología</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1100px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #38bdf8;
            font-size: 24px;
            margin-bottom: 4px;
        }
        p.subtitle {
            text-align: center;
            color: #94a3b8;
            font-size: 13px;
            margin-bottom: 25px;
        }
        
        /* Tarjetas de Indicadores (KPIs) */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .kpi-card {
            background-color: #1e293b;
            border-left: 4px solid #38bdf8;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }
        .kpi-title {
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 20px;
            font-weight: bold;
            color: #f8fafc;
        }

        /* Gráficas */
        .grid-charts {
            display: grid;
            grid-template-columns: 1fr;
            gap:
