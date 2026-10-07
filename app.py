from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def inicio():
    return "¡Mi servidor Python está funcionando!"

@app.route("/analitica")
def analitica():
    # Datos para cumplir la analítica 
    datos = {
        "status": "exito",
        "modulo": "Analítica de Datos",
        "resultados": [
            {"categoria": "Ventas", "valor": 150},
            {"categoria": "Usuarios", "valor": 45}
        ]
    }
    return jsonify(datos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
