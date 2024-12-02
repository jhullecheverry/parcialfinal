from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import random

# Inicializar la app de Flask
app = Flask(__name__)

# Inicializar Firebase con Realtime Database
cred = credentials.Certificate("C:/Users/jhoja/parcial/dyno-a7d44-firebase-adminsdk-yidim-1fd4ab9335.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://dyno-a7d44-default-rtdb.firebaseio.com/'
})

# Lista de modelos de carros para generar IDs aleatorios
MODELOS_CARROS = [
    # Modelos M de BMW
    "BMW M2", "BMW M3", "BMW M4", "BMW M5", "BMW M6", 
    "BMW M8", "BMW X3 M", "BMW X4 M", "BMW X5 M", "BMW X6 M",
    # Autos deportivos de gama media y alta
    "Toyota GR Supra", "Nissan GT-R", "Chevrolet Corvette", "Ford Mustang Shelby GT500", 
    "Porsche 911 Carrera", "Porsche 718 Cayman", "Audi R8", "Mercedes-Benz AMG GT", 
    "Lexus LC 500", "Dodge Challenger SRT Hellcat", "Tesla Roadster",
    "Ferrari 488 GTB", "Ferrari F8 Tributo", "Lamborghini Huracán", 
    "Lamborghini Aventador", "McLaren 720S", "McLaren Artura", 
    "Aston Martin DB11", "Aston Martin Vantage", "Jaguar F-Type R", 
    "Maserati GranTurismo", "Alfa Romeo 4C Spider", "Lotus Evora GT", 
    "Koenigsegg Jesko", "Pagani Huayra", "Bugatti Chiron", 
    "Bugatti Veyron", "Ford GT", "Rimac Nevera", "Hennessey Venom F5",
    # Otros modelos deportivos icónicos
    "Subaru WRX STI", "Mitsubishi Lancer Evo X", "Hyundai N Vision 74", 
    "Kia Stinger GT", "Chevrolet Camaro ZL1"
]

# Función para generar un modelo de carro aleatorio
def generar_modelo_carro():
    return random.choice(MODELOS_CARROS)
    
@app.route('/analisis')
def analisis():
    try:
        ref = db.reference('sensores')
        datos = ref.get() or {}  # Manejo si no hay datos
        sensores = set(item['idsensor'] for item in datos.values() if 'idsensor' in item)
        return render_template('analisis.html', sensores=list(sensores))
    except Exception as e:
        return jsonify({"error": f"Error al cargar datos: {str(e)}"}), 500
@app.route('/api/fechas', methods=['GET'])
def obtener_fechas():
    try:
        idsensor = request.args.get('idsensor')
        if not idsensor:
            return jsonify({"error": "Se requiere el parámetro 'idsensor'"}), 400

        # Obtener datos de Firebase
        ref = db.reference('sensores')
        datos = ref.get() or {}
        
        # Filtrar las fechas únicas para el sensor dado
        fechas = set(dato['fecha'] for dato in datos.values() if dato.get('idsensor') == idsensor)
        
        return jsonify(sorted(fechas))  # Devolver las fechas ordenadas
    except Exception as e:
        return jsonify({"error": f"Error al obtener fechas: {str(e)}"}), 500

# Ruta principal para mostrar la interfaz web
@app.route('/')
def index():
    try:
        # Obtener la fecha y hora actual
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        hora_actual = datetime.now().strftime("%H:%M:%S")
        
        # Generar un modelo de carro aleatorio
        id_modelo = generar_modelo_carro()
        
        # Obtener los datos de Realtime Database
        ref = db.reference('sensores')
        datos = ref.get()  # Obtener todos los datos almacenados en 'sensores'

        # Renderizar la plantilla HTML con los datos generados y almacenados
        return render_template(
            'index.html',
            fecha=fecha_actual,
            hora=hora_actual,
            id_modelo=id_modelo,
            datos=datos
        )
    except Exception as e:
        # Manejo de errores si hay problemas al conectar con Firebase
        return jsonify({"error": f"No se pudo cargar los datos: {str(e)}"}), 500

# Ruta para recibir y guardar datos de los sensores
@app.route('/api/sensor', methods=['POST'])
def recibir_datos():
    try:
        # Validar que el Content-Type sea application/json
        if request.content_type != 'application/json':
            return jsonify({"error": "El Content-Type debe ser 'application/json'"}), 415

        # Obtener los datos en formato JSON
        datos = request.get_json()

        # Validar que los datos contienen todos los campos requeridos
        campos_requeridos = ['id', 'fecha', 'hora', 'idsensor', 'valor']
        if not all(campo in datos for campo in campos_requeridos):
            return jsonify({"error": "Faltan campos requeridos. Campos esperados: id, fecha, hora, idsensor, valor"}), 400

        # Validar que los valores no estén vacíos
        for campo in campos_requeridos:
            if not datos[campo]:
                return jsonify({"error": f"El campo '{campo}' no puede estar vacío"}), 400

        # Validar que el valor sea un número (si aplica)
        try:
            datos['valor'] = float(datos['valor'])
        except ValueError:
            return jsonify({"error": "El campo 'valor' debe ser un número"}), 400

        # Almacenar los datos en Realtime Database
        ref = db.reference('sensores')
        ref.push(datos)  # Agregar los datos como un nuevo nodo

        return jsonify({"mensaje": "Datos almacenados correctamente"}), 201

    except Exception as e:
        # Manejo de errores inesperados
        return jsonify({"error": f"Error al procesar los datos: {str(e)}"}), 500
    
@app.route('/api/datos', methods=['GET'])
def obtener_datos():
    try:
        # Obtener los parámetros
        idsensor = request.args.get('idsensor')
        fecha = request.args.get('fecha')

        if not idsensor or not fecha:
            app.logger.error("Parámetros faltantes: idsensor=%s, fecha=%s", idsensor, fecha)
            return jsonify({"error": "Se requieren parámetros 'idsensor' y 'fecha'"}), 400

        # Leer datos de Firebase
        ref = db.reference('sensores')
        datos = ref.get() or {}

        app.logger.debug("Datos obtenidos desde Firebase: %s", datos)

        # Filtrar datos por sensor y fecha
        datos_filtrados = [
            {
                "id": key,
                "idsensor": dato.get('idsensor'),
                "fecha": dato.get('fecha'),
                "hora": dato.get('hora'),
                "valor": dato.get('valor')
            }
            for key, dato in datos.items()
            if dato.get('idsensor') == idsensor and dato.get('fecha') == fecha
        ]

        app.logger.debug("Datos filtrados: %s", datos_filtrados)

        return jsonify(datos_filtrados)
    except Exception as e:
        app.logger.error("Error al procesar datos: %s", str(e))
        return jsonify({"error": f"Error al procesar datos: {str(e)}"}), 500

# Ejecutar la app
if __name__ == "__main__":
    app.run(debug=True)


