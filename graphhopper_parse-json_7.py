import requests
import urllib.parse

# URL base y clave de Graphhopper
route_url = "https://graphhopper.com/api/1/route?"
key = "325f5b21-31d2-4191-be43-a0598d8c115e"  # Reemplaza por tu propia API key si es necesario


def geocodificar(ubicacion, key):
    """Función para obtener coordenadas (lat, lng) desde una ubicación."""
    while ubicacion == "":
        ubicacion = input("Ingrese nuevamente la ubicación: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": ubicacion, "limit": "1", "key": key})

    respuesta = requests.get(url)
    datos = respuesta.json()
    estado = respuesta.status_code

    if estado == 200 and len(datos["hits"]) != 0:
        lat = datos["hits"][0]["point"]["lat"]
        lng = datos["hits"][0]["point"]["lng"]
        nombre = datos["hits"][0]["name"]
        valor = datos["hits"][0]["osm_value"]

        pais = datos["hits"][0].get("country", "")
        estado_local = datos["hits"][0].get("state", "")

        if estado_local and pais:
            nueva_ubicacion = f"{nombre}, {estado_local}, {pais}"
        elif pais:
            nueva_ubicacion = f"{nombre}, {pais}"
        else:
            nueva_ubicacion = nombre

        print(f"URL de la API de Geocodificación para {nueva_ubicacion} (Tipo: {valor})\n{url}")
    else:
        lat = "null"
        lng = "null"
        nueva_ubicacion = ubicacion
        if estado != 200:
            print(f"Estado de la API de Geocodificación: {estado}\nMensaje de error: {datos['message']}")

    return estado, lat, lng, nueva_ubicacion


while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Perfiles de vehículo disponibles en Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("auto, bicicleta, a pie")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    perfiles = ["car", "bike", "foot"]

    vehiculo = input("Ingrese un perfil de vehículo de la lista anterior (o escriba 's' para salir): ").lower()
    if vehiculo in ["salir", "s"]:
        print("Saliendo del programa...")
        break
    elif vehiculo in ["auto", "car"]:
        vehiculo = "car"
    elif vehiculo in ["bicicleta", "bike"]:
        vehiculo = "bike"
    elif vehiculo in ["pie", "foot"]:
        vehiculo = "foot"
    else:
        vehiculo = "car"
        print("No se ingresó un perfil válido. Se usará el perfil por defecto: auto.")

    loc1 = input("Ingrese la ubicación de inicio: ")
    if loc1 in ["salir", "s"]:
        print("Saliendo del programa...")
        break
    origen = geocodificar(loc1, key)

    loc2 = input("Ingrese el destino: ")
    if loc2 in ["salir", "s"]:
        print("Saliendo del programa...")
        break
    destino = geocodificar(loc2, key)

    print("=================================================")
    if origen[0] == 200 and destino[0] == 200:
        op = f"&point={origen[1]}%2C{origen[2]}"
        dp = f"&point={destino[1]}%2C{destino[2]}"

        # Agregamos locale=es para obtener instrucciones en español
        parametros = {"key": key, "vehicle": vehiculo, "locale": "es"}
        paths_url = route_url + urllib.parse.urlencode(parametros) + op + dp

        respuesta_ruta = requests.get(paths_url)
        estado_ruta = respuesta_ruta.status_code
        datos_ruta = respuesta_ruta.json()

        print(f"Estado de la API de Rutas: {estado_ruta}\nURL utilizada:\n{paths_url}")
        print("=================================================")
        print(f"Direcciones desde {origen[3]} hasta {destino[3]} usando {vehiculo}")
        print("=================================================")

        if estado_ruta == 200:
            km = datos_ruta["paths"][0]["distance"] / 1000
            millas = km / 1.61
            seg = int(datos_ruta["paths"][0]["time"] / 1000 % 60)
            min_ = int(datos_ruta["paths"][0]["time"] / 1000 / 60 % 60)
            hr = int(datos_ruta["paths"][0]["time"] / 1000 / 60 / 60)

            print(f"Distancia recorrida: {millas:.2f} millas / {km:.2f} km")
            print(f"Duración del viaje: {hr:02d}:{min_:02d}:{seg:02d}")
            print("=================================================")
            print("Instrucciones del recorrido:")
            print("-------------------------------------------------")

            for paso in datos_ruta["paths"][0]["instructions"]:
                texto = paso["text"]
                distancia = paso["distance"]
                print(f"{texto} ({distancia/1000:.2f} km / {distancia/1000/1.61:.2f} millas)")

            print("=================================================")
        else:
            print(f"Mensaje de error: {datos_ruta.get('message', 'Error desconocido')}")
            print("*************************************************")
    else:
        print("No se pudieron obtener las coordenadas de las ubicaciones ingresadas.")
