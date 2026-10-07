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

# --- 2. PLANTILLA HTML ---
HTML_TEMPLATE = (
    "<!DOCTYPE html>\n"
    "<html lang='es'>\n"
    "<head>\n"
    "    <meta charset='UTF-8'>\n"
    "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
    "    <title>Base de Datos - Tienda de Tecnología</title>\n"
    "    <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>\n"
    "    <style>\n"
    "        body { font-family: 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }\n"
    "        .container { max-width: 1100px; margin: 0 auto; }\n"
    "        h1 { text-align: center; color: #38bdf8; font-size: 24px; margin-bottom: 4px; }\n"
    "        p.subtitle { text-align: center; color: #94a3b8; font-size: 13px; margin-bottom: 25px; }\n"
    "        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }\n"
    "        .kpi-card { background-color: #1e293b; border-left: 4px solid #38bdf8; border-radius: 8px; padding: 15px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }\n"
    "        .kpi-title { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }\n"
    "        .kpi-value { font-size: 20px; font-weight: bold; color: #f8fafc; }\n"
    "        .grid-charts { display: grid; grid-template-columns: 1fr; gap: 20px; margin-bottom: 20px; }\n"
    "        @media(min-width: 768px) { .grid-charts { grid-template-columns: 1fr 1fr; } }\n"
    "        .card { background-color: #1e293b; border-radius: 10px; padding: 18px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }\n"
    "        h2 { color: #f1f5f9; font-size: 15px; margin-top: 0; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 15px; }\n"
    "        .chart-container { position: relative; height: 250px; width: 100%; }\n"
    "        .search-box { width: 100%; padding: 10px; background-color: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #f8fafc; box-sizing: border-box; margin-bottom: 15px; font-size: 13px; }\n"
    "        .search-box:focus { outline: none; border-color: #38bdf8; }\n"
    "        .table-responsive { overflow-x: auto; }\n"
    "        table { width: 100%; border-collapse: collapse; font-size: 12px; }\n"
    "        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #334155; }\n"
    "        th { background-color: #334155; color: #38bdf8; font-weight: 600; }\n"
    "        tr:hover { background-color: #243248; }\n"
    "        .badge { background-color: #0284c7; padding: 3px 8px; border-radius: 12px; font-size: 11px; }\n"
    "        .status-ok { color: #34d399; font-weight: bold; }\n"
    "        .status-low { color: #f87171; font-weight: bold; }\n"
    "    </style>\n"
    "</head>\n"
    "<body>\n"
    "    <div class='container'>\n"
    "        <h1>Base de Datos - Tienda de Tecnología</h1>\n"
    "        <p class='subtitle'>Sistema de gestión relacional en SQLite y visualización interactiva</p>\n"
    "        <div class='kpi-grid'>\n"
    "            <div class='kpi-card'><div class='kpi-title'>Ventas Totales</div><div class='kpi-value'>${{ '%.2f'|format(total_ingresos) }}</div></div>\n"
    "            <div class='kpi-card'><div class='kpi-title'>Unidades Vendidas</div><div class='kpi-value'>{{ total_unidades }} pcs</div></div>\n"
    "            <div class='kpi-card'><div class='kpi-title'>Promedio por Venta</div><div class='kpi-value'>${{ '%.2f'|format(promedio_venta) }}</div></div>\n"
    "            <div class='kpi-card'><div class='kpi-title'>Producto Más Vendido</div><div class='kpi-value' style='font-size: 14px; margin-top: 5px;'>{{ producto_top }}</div></div>\n"
    "        </div>\n"
    "        <div class='grid-charts'>\n"
    "            <div class='card'><h2>Ingresos por Categoría</h2><div class='chart-container'><canvas id='barChart'></canvas></div></div>\n"
    "            <div class='card'><h2>Distribución por Método de Pago</h2><div class='chart-container'><canvas id='pieChart'></canvas></div></div>\n"
    "        </div>\n"
    "        <div class='card'>\n"
    "            <h2>Tabla Relacional `ventas` (SQLite)</h2>\n"
    "            <input type='text' id='searchInput' onkeyup='filterTable()' placeholder='Buscar producto, categoría o método de pago...' class='search-box'>\n"
    "            <div class='table-responsive'>\n"
    "                <table id='ventasTable'>\n"
    "                    <thead>\n"
    "                        <tr><th>ID</th><th>Producto</th><th>Categoría</th><th>Precio Univ.</th><th>Cantidad</th><th>Método Pago</th><th>Monto Total</th><th>Estatus Stock</th></tr>\n"
    "                    </thead>\n"
    "                    <tbody>\n"
    "                        {% for fila in ventas_lista %}\n"
    "                        <tr>\n"
    "                            <td><code>#{{ fila.id }}</code></td>\n"
    "                            <td><strong>{{ fila.producto }}</strong></td>\n"
    "                            <td><span class='badge'>{{ fila.categoria }}</span></td>\n"
    "                            <td>${{ '%.2f'|format(fila.precio) }}</td>\n"
    "                            <td>{{ fila.cantidad }}</td>\n"
    "                            <td>{{ fila.metodo_pago }}</td>\n"
    "                            <td><strong>${{ '%.2f'|format(fila.monto_total) }}</strong></td>\n"
    "                            <td>\n"
    "                                {% if fila.stock < 5 %}\n"
    "                                    <span class='status-low'>Bajo Stock ({{ fila.stock }})</span>\n"
    "                                {% else %}\n"
    "                                    <span class='status-ok'>En Stock ({{ fila.stock }})</span>\n"
    "                                {% endif %}\n"
    "                            </td>\n"
    "                        </tr>\n"
    "                        {% endfor %}\n"
    "                    </tbody>\n"
    "                </table>\n"
    "            </div>\n"
    "        </div>\n"
    "    </div>\n"
    "    <script>\n"
    "        const ctxBar = document.getElementById('barChart').getContext('2d');\n"
    "        new Chart(ctxBar, {\n"
    "            type: 'bar',\n"
    "            data: {\n"
    "                labels: {{ categorias | tojson }},\n"
    "                datasets: [{\n"
    "                    label: 'Ventas Total ($)',\n"
    "                    data: {{ montos_cat | tojson }},\n"
    "                    backgroundColor: '#38bdf8',\n"
    "                    borderColor: '#0284c7',\n"
    "                    borderWidth: 1,\n"
    "                    borderRadius: 4\n"
    "                }]\n"
    "            },\n"
    "            options: {\n"
    "                responsive: true,\n"
    "                maintainAspectRatio: false,\n"
    "                scales: {\n"
    "                    y: { beginAtZero: true, ticks: { color: '#f8fafc' }, grid: { color: '#334155' } },\n"
    "                    x: { ticks: { color: '#f8fafc' }, grid: { color: '#334155' } }\n"
    "                },\n"
    "                plugins: { legend: { display: false } }\n"
    "            }\n"
    "        });\n"
    "        const ctxPie = document.getElementById('pieChart').getContext('2d');\n"
    "        new Chart(ctxPie, {\n"
    "            type: 'pie',\n"
    "            data: {\n"
    "                labels: {{ metodos | tojson }},\n"
    "                datasets: [{\n"
    "                    data: {{ montos_pago | tojson }},\n"
    "                    backgroundColor: ['#38bdf8', '#818cf8', '#34d399'],\n"
    "                    borderWidth: 1,\n"
    "                    borderColor: '#1e293b'\n"
    "                }]\n"
    "            },\n"
    "            options: {\n"
    "                responsive: true,\n"
    "                maintainAspectRatio: false,\n"
    "                plugins: {\n"
    "                    legend: { position: 'bottom', labels: { color: '#f8fafc' } }\n"
    "                }\n"
    "            }\n"
    "        });\n"
    "        function filterTable() {\n"
    "            const input = document.getElementById('searchInput');\n"
    "            const filter = input.value.toLowerCase();\n"
    "            const table = document.getElementById('ventasTable');\n"
    "            const tr = table.getElementsByTagName('tr');\n"
    "            for (let i = 1; i < tr.length; i++) {\n"
    "                let rowText = tr[i].textContent.toLowerCase();\n"
    "                if (rowText.indexOf(filter) > -1) {\n"
    "                    tr[i].style.display = '';\n"
    "                } else {\n"
    "                    tr[i].style.display = 'none';\n"
    "                }\n"
    "            }\n"
    "        }\n"
    "    </script>\n"
    "</body>\n"
    "</html>"
)

# --- 3. RUTAS FLASK ---
@app.route("/")
def dashboard():
    conn = sqlite3.connect('tienda.db')
    
    df_ventas = pd.read_sql_query("SELECT * FROM ventas ORDER BY monto_total DESC", conn)
    ventas_lista = df_ventas.to_dict(orient='records')
    
    total_ingresos = df_ventas['monto_total'].sum()
    total_unidades = int(df_ventas['cantidad'].sum())
    promedio_venta = df_ventas['monto_total'].mean()
    
    top_row = df_ventas.sort_values(by='cantidad', ascending=False).iloc[0]
    producto_top = f"{top_row['producto']} ({top_row['cantidad']} uds)"
    
    df_cat = pd.read_sql_query("SELECT categoria, SUM(monto_total) as total FROM ventas GROUP BY categoria ORDER BY total DESC", conn)
    categorias = df_cat['categoria'].tolist()
    montos_cat = df_cat['total'].tolist()
    
    df_pago = pd.read_sql_query("SELECT metodo_pago, SUM(monto_total) as total FROM ventas GROUP BY metodo_pago", conn)
    metodos = df_pago['metodo_pago'].tolist()
    montos_pago = df_pago['total'].tolist()
    
    conn.close()
    
    return render_template_string(
        HTML_TEMPLATE, 
        ventas
