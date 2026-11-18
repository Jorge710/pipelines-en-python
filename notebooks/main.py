
from flask import Flask

# Importar las versiones
import version_1
import version_2

app = Flask(__name__)


@app.route("/")
def inicio():

    print("Iniciando ejecución de pipelines")

    # Ejecutar versión 1
    #resultado = version_1.ejecutar()
    resultado = version_2.ejecutar()

    return f"""
        <h1>PIPELINES EN PYTHON</h1>
        <h2>Ejecutando proyecto en Docker</h2>
        <p>Pipeline ejecutado correctamente.</p>
        <p>Resultado: {resultado}</p>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
