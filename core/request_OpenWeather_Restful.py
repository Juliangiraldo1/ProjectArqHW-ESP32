# importamos librerias necesarias
import machine #acceder al esp32
import network #manejo del wifi
import urequests #consumo get
import ujson as json
import time

#---------------------------------------------------
#Configuracion ESP32 wifi
sta= network.WLAN(network.STA_IF)
if not sta.isconnected():
    print('conectando al wifi...')
    sta.active(True)
    sta.connect('iPhone de Julian', 'Julian1704')
    while not sta.isconnected():
        pass
print('network config:', sta.ifconfig())

#---------------------------------------------------
#Configurar constantes empleadas en el consumo
#https://api.openweathermap.org/data/2.5/weather?q=medellin&appid=eeedf04d6a058369c4bed830801d77d0
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "eeedf04d6a058369c4bed830801d77d0"
CITY_NAME = "medellin"
URL= BASE_URL + "q=" + CITY_NAME + "&appid=" + API_KEY

UPDATE_INTERVALE_ms= 60000
last_update = time.ticks_ms()


# **************************************
# Main
while True:
    if time.ticks_ms() - last_update >= UPDATE_INTERVALE_ms:
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

            #obtenemos porcentaje de humedad
            humidity = main['humidity']

            # Obtenemos presion en hPA
            pressure = main['pressure']

            # reporte completo del clima
            report = data['weather']

            print('')
            print('**OpenWeather**')
            print('Ciudad:{}' .format(CITY_NAME))
            print('Temperatura:{} oC' .format(temperature))
            print('Humedad:{} %' .format(humidity))
            print('Presion:{} hPa' .format(pressure))
            print('Reporte del clima:{}.' .format(report[0]['description']))
        else:
            # Mensaje de error al consumir api
            print('Error in HTTP request.')
        last_update = time.ticks_ms()
