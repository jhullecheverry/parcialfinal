import requests
import random
import time
from datetime import datetime

# URL de la API Flask
URL_API = "http://127.0.0.1:5000/api/sensor"  # Cambiar a la URL del servidor si es diferente

# Lista de modelos de vehículos definida en el archivo app.py
MODELOS_CARROS = [
    "BMW M2", "BMW M3", "BMW M4", "BMW M5", "BMW M6", 
    "BMW M8", "BMW X3 M", "BMW X4 M", "BMW X5 M", "BMW X6 M",
    "Toyota GR Supra", "Nissan GT-R", "Chevrolet Corvette", "Ford Mustang Shelby GT500", 
    "Porsche 911 Carrera", "Porsche 718 Cayman", "Audi R8", "Mercedes-Benz AMG GT", 
    "Lexus LC 500", "Dodge Challenger SRT Hellcat", "Tesla Roadster",
    "Ferrari 488 GTB", "Ferrari F8 Tributo", "Lamborghini Huracán", 
    "Lamborghini Aventador", "McLaren 720S", "McLaren Artura", 
    "Aston Martin DB11", "Aston Martin Vantage", "Jaguar F-Type R", 
    "Maserati GranTurismo", "Alfa Romeo 4C Spider", "Lotus Evora GT", 
    "Koenigsegg Jesko", "Pagani Huayra", "Bugatti Chiron", 
    "Bugatti Veyron", "Ford GT", "Rimac Nevera", "Hennessey Venom F5",
    "Subaru WRX STI", "Mitsubishi Lancer Evo X", "Hyundai N Vision 74", 
    "Kia Stinger GT", "Chevrolet Camaro ZL1"
]

# Función para generar datos aleatorios del sensor
def generar_datos_sensor():
    modelo = random.choice(MODELOS_CARROS)  # Seleccionar un modelo de vehículo aleatorio
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    hora_actual = datetime.now().strftime("%H:%M:%S")
    valor_aleatorio = round(random.uniform(15.0, 100.0), 2)  # Generar valor aleatorio

    return {
        "id": modelo,  # Usar el modelo como ID
        "fecha": fecha_actual,  # Fecha actual
        "hora": hora_actual,  # Hora actual
        "idsensor": f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}{random.randint(100, 999)}",  # ID del sensor aleatorio
        "valor": valor_aleatorio  # Valor aleatorio
    }

# Función principal para simular el envío de datos
def simular_envio():
    while True:
        try:
            # Generar datos del sensor
            datos = generar_datos_sensor()
            
            # Enviar los datos a la API
            respuesta = requests.post(URL_API, json=datos)
            
            # Verificar el estado de la respuesta
            if respuesta.status_code == 201:
                print(f"Datos enviados correctamente: {datos}")
            else:
                print(f"Error al enviar datos: {respuesta.status_code} - {respuesta.json()}")
        
        except Exception as e:
            print(f"Error al conectar con la API: {str(e)}")
        
        # Esperar 3 segundos antes de enviar los siguientes datos
        time.sleep(3)

# Ejecutar la simulación
if __name__ == "__main__":
    simular_envio()
