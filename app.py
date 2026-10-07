from flask import Flask, render_template_string
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
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Base de Datos - Tienda de Tecnología</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 1100px; margin: 0 auto; }
        h1 { text-align: center; color: #38bdf8; font-size: 24px; margin-bottom: 5px; }
        p.subtitle { text-align: center; color: #94a3b8; font-size: 13px; margin-bottom: 25px; }
        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .kpi-card { background-color: #1e293b; border-left: 4px solid #38bdf8; border-radius: 8px; padding: 15px; }
        .kpi-title { font-size: 11px; color: #94a3b8; text-transform: uppercase; margin-bottom: 5px; }
        .kpi-value { font-size: 20px; font-weight: bold; color: #f8fafc; }
        .grid-charts { display: grid; grid-template-columns: 1fr; gap: 20px; margin-bottom: 20px; }
        @media(min-width: 768px) { .grid-charts { grid-template-columns: 1fr 1fr; } }
        .card { background-color: #1e293b; border-radius: 10px; padding: 18px; }
        h2 { color: #f1f5f9; font-size: 15px; margin-top: 0; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 15px; }
        .chart-container { position: relative; height: 250px; width: 100%; }
        .search-box { width: 100%; padding: 10px; background-color: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #f8fafc; box-sizing: border-box; margin-bottom: 15px; font-size: 13px; }
        .table-responsive { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #334155; }
        th { background-color: #334155; color: #38bdf8; }
        tr:hover { background-color: #243248; }
        .badge { background-color: #0284c7; padding: 3px 8px; border-radius: 12px; font-size: 11px; }
        .status-ok { color: #34d399; font-weight: bold; }
        .status-low { color: #f87171; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Base de Datos - Tienda de Tecnología</h1>
        <p class="subtitle">Sistema de gestión relacional en SQLite y visualización interactiva</p>

        <div class="kpi-grid">
            <div class="kpi-card"><div class="kpi-title">Ventas Totales</div><div class="kpi-value">${{ total_ingresos }}</div></div>
            <div class="kpi-card"><div class="kpi-title">Unidades Vendidas</div><div class="kpi-value">{{ total_unidades }} pcs</div></div>
            <div class="kpi-card"><div class="kpi-title">Promedio por Venta</div><div class="kpi-value">${{ promedio_venta }}</div></div>
            <div class="kpi-card"><div class="kpi-title">Producto Más Vendido</div><div class="kpi-value" style="font-size: 14px; margin-top: 5px;">{{ producto_top }}</div></div>
        </div>

        <div class="grid-charts">
            <div class="card"><h2>Ingresos por Categoría</h2><div class="chart-container"><canvas id="barChart"></canvas></div></div>
            <div class="card"><h2>Distribución por Método de Pago</h2><div class="chart-container"><canvas id="pieChart"></canvas></div></div>
        </div>

        <div class="card">
            <h2>Tabla Relacional `ventas` (SQLite)</h2>
            <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Buscar producto, categoría o método de pago..." class="search-box">
            <div class="table-responsive">
                <table id="ventasTable">
                    <thead>
                        <tr><th>ID</th><th>Producto</th><th>Categoría</th><th>Precio Univ.</th><th>Cantidad</th><th>Método Pago</th><th>Monto Total</th><th>Estatus Stock</th></tr>
                    </thead>
                    <tbody>
                        {% for fila in ventas_lista %}
                        <tr>
                            <td><code>#{{ fila.id }}</code></td>
                            <td><strong>{{ fila.producto }}</strong></td>
                            <td><span class="badge">{{ fila.categoria }}</span></td>
                            <td>${{ fila.precio }}</td>
                            <td>{{ fila.cantidad }}</td>
                            <td>{{ fila.metodo_pago }}</td>
                            <td><strong>${{ fila.monto_total }}</strong></td>
                            <td>
                                {% if fila.stock < 5 %}
                                    <span class="status-low">Bajo Stock ({{ fila.stock }})</span>
                                {% else %}
                                    <span class="status-ok">En Stock ({{ fila.stock }})</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const ctxBar = document.getElementById('barChart').getContext('2d');
        new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: {{ categorias | tojson }},
                datasets: [{
                    label: 'Ventas Total ($)',
                    data: {{ montos_cat | tojson }},
                    backgroundColor: '#38bdf8',
                    borderColor: '#0284c7',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#f8fafc' }, grid: { color: '#334155' } },
                    x: { ticks: { color: '#f8fafc' }, grid: { color: '#334155' } }
                },
                plugins: { legend: { display: false } }
            }
        });

        const ctxPie = document.getElementById('pieChart').getContext('2d');
        new Chart(ctxPie, {
            type: 'pie',
            data: {
                labels: {{ metodos | tojson }},
                datasets: [{
                    data: {{ montos_pago | tojson }},
                    backgroundColor: ['#38bdf8', '#818cf8', '#34d399'],
                    borderWidth: 1,
                    borderColor: '#1e293b'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#f8fafc' } }
                }
            }
        });

        function filterTable() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const table = document.getElementById('ventasTable');
            const tr = table.getElementsByTagName('tr');
            for (let i = 1; i < tr.length; i++) {
                let rowText = tr[i].textContent.toLowerCase();
                tr[i].style.display = rowText.indexOf(filter) > -1 ? '' : 'none';
            }
        }
    </script>
</body>
</html>"""

# --- 3. RUTAS FLASK ---
@app.route("/")
def dashboard():
    conn = sqlite3.connect('tienda.db')
    
    df_ventas = pd.read_sql_query("SELECT * FROM ventas ORDER BY monto_total DESC", conn)
    ventas_lista = df_ventas.to_dict(orient='records')
    
    total_ingresos = round(float(df_ventas['monto_total'].sum()), 2)
    total_unidades = int(df_ventas['cantidad'].sum())
    promedio_venta = round(float(df_ventas['monto_total'].mean()), 2)
    
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
        ventas_lista=ventas_lista,
        total_ingresos=total_ingresos,
        total_unidades=total_unidades,
        promedio_venta=promedio_venta,
        producto_top=producto_top,
        categorias=categorias,
        montos_cat=montos_cat,
        metodos=metodos,
        montos_pago=montos_pago
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
