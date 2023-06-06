# importamos librerias necesarias
import machine  # acceder al esp32
import network  # manejo del wifi
import urequests  # consumo get
import ujson as json
import time
"""---------------------------------------------------"""
# Configuracion ESP32 wifi
sta = network.WLAN(network.STA_IF)
if not sta.isconnected():
    print('conectando al wifi...')
    sta.active(True)
    sta.connect('Wifi Gratis', '43645172')
    while not sta.isconnected():
        pass
print('network config:', sta.ifconfig())

# ---------------------------------------------------
# Configurar constantes empleadas en el consumo
# https://api.openweathermap.org/data/2.5/weather?q=medellin&appid=eeedf04d6a058369c4bed830801d77d0
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "eeedf04d6a058369c4bed830801d77d0"
CITY_NAME = "medellin"
URL = BASE_URL + "q=" + CITY_NAME + "&appid=" + API_KEY

UPDATE_INTERVALE_ms = 30000
last_update = time.ticks_ms()
# cofigurar el bot de TELEGRAM
# bot = telebot.Telebot("6173394954:AAFN9HOLGQwBqltNr3Z3L_QiXgoywYqRSt4")
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    headers = {"Content-Type": "application/json"}
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = urequests.post(url, data=json.dumps(payload), headers=headers)
    response.close()

# Configura el token y el chat ID
token = "6173394954:AAFN9HOLGQwBqltNr3Z3L_QiXgoywYqRSt4"
chat_id = "-962636275"

# Envía un mensaje de prueba

# **************************************
# Main
while True:
    if time.ticks_ms() - last_update >= UPDATE_INTERVALE_ms:
        """-------------------------- datos de sensor de proximidad----------------------------------- """
        # Configura el pin del sensor de proximidad
        sensor_pin = machine.Pin(25, machine.Pin.IN)  # como es de entrada por eso lleva IN
        # valores que arroja el sensor: Low == 0 activa sensor en acso contrario de High == 1.
        # print("Valor INICIAL Del sensor = ", sensor_pin.value())
        for _ in range(4):
            if sensor_pin.value() == 0:
                print("¡Mascota detectada!")
                print(sensor_pin.value())
                # time.sleep(5)  # espera  segundos
                send_telegram_message(token, chat_id, "¡Hola, se acerco la mascota!")
            else:
                print("¡ No hay !")
                print(sensor_pin.value())
                # time.sleep(5)  # espera  segundos
            print("¡ESPERARA 5 SEGUNDOS para ejecutarse de nuevo!")
            time.sleep(5)  # espera  5 segundos
        """------------------------------------------------------------- """
        print("Desconectarse")
        time.sleep(5)  # Espera segundos
        # se envia peticion al api y se almacena en response
        response = urequests.get(URL)
        if response.status_code == 200:
            # obtenemos json en formato data
            data = response.json()

            # obtenemos main de la data
            main = data['main']

            # Obtenemos temperatura
            # 273.15 se reta para obtener la temp en Celcius
            # El valor original de temp es en Kelvin
            temperature = main['temp'] - 273.15

            if temperature > 0:
                # -----------------------------------------------------
                # Configuramos datos para servomotor
                # Configura el pin GPIO donde está conectado el servo
                pin_servo = machine.Pin(33)
                servo = machine.PWM(pin_servo)

                # Configura los límites del pulso del servo (ajusta según tu servo)
                servo.freq(50)
                servo.duty_ns(500000)  # 0 grados

                # Repite el movimiento del servo 10 veces
                for _ in range(1):
                    # Mueve el servo a 90 grados
                    servo.duty_ns(1500000)  # 90 grados
                    time.sleep(5.0)

                    # Mueve el servo a 0 grados
                    servo.duty_ns(500000)  # 0 grados
                    time.sleep(0.5)
                    send_telegram_message(token, chat_id, "¡Hola, se alimento la mascota!")
                # Detiene el PWM y libera el pin
                servo.deinit()
                # ---------------------------------------------------------

            # obtenemos porcentaje de humedad
            humidity = main['humidity']

            # Obtenemos presion en hPA
            pressure = main['pressure']

            # reporte completo del clima
            report = data['weather']

            print('')
            print('**Respuesta API OpenWeather**')
            print('Ciudad:{}' .format(CITY_NAME))
            print('Temperatura:{} oC' .format(temperature))
            print('Humedad:{} %' .format(humidity))
            print('Presion:{} hPa' .format(pressure))
            print('Reporte del clima:{}.' .format(report[0]['description']))

        else:
            # Mensaje de error al consumir api
            print('Error in HTTP request.')
        last_update = time.ticks_ms()
