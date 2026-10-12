from flask import Flask, render_template
import sqlite3
import pandas as pd

app = Flask(__name__)

# --- BASE DE DATOS SQLITE (TIENDA DE TECNOLOGÍA) ---
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

# --- RUTAS FLASK ---
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
    
    return render_template(
        'index.html',
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
