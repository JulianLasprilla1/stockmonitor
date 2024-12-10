from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import os
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Variables de entorno
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Simulación de almacenamiento de tokens (reemplazar con base de datos en producción)
TOKEN_STORAGE = {
    "access_token": None,
    "refresh_token": None,
    "expires_at": None,
}

# Funciones auxiliares para manejo de tokens
def refresh_access_token():
    """Renueva el Access Token usando el Refresh Token"""
    if not TOKEN_STORAGE["refresh_token"]:
        return None

    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": TOKEN_STORAGE["refresh_token"],
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        TOKEN_STORAGE["access_token"] = token_data["access_token"]
        TOKEN_STORAGE["refresh_token"] = token_data["refresh_token"]
        TOKEN_STORAGE["expires_at"] = datetime.now() + timedelta(seconds=token_data["expires_in"])
        return TOKEN_STORAGE["access_token"]
    else:
        print("Error al renovar el token:", response.json())
        return None

def get_valid_access_token():
    """Devuelve un Access Token válido, renueva si es necesario"""
    if TOKEN_STORAGE["access_token"] and TOKEN_STORAGE["expires_at"] > datetime.now():
        return TOKEN_STORAGE["access_token"]
    else:
        return refresh_access_token()

@app.route("/")
def home():
    return jsonify({"message": "API de StockMonitor funcionando correctamente"})

@app.route("/auth")
def auth():
    """Redirige al usuario para autorizar la aplicación"""
    auth_url = f"https://auth.mercadolibre.com.co/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    return redirect(auth_url)

@app.route("/callback")
def callback():
    """Callback para manejar el código de autorización"""
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "No se recibió el código de autorización"}), 400

    # Intercambiar el código por un access_token
    token_url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(token_url, data=payload)
    token_data = response.json()

    if "access_token" in token_data:
        TOKEN_STORAGE["access_token"] = token_data["access_token"]
        TOKEN_STORAGE["refresh_token"] = token_data.get("refresh_token")
        TOKEN_STORAGE["expires_at"] = datetime.now() + timedelta(seconds=token_data["expires_in"])
        return jsonify({"message": "Autenticación exitosa", "token_data": token_data})
    else:
        return jsonify({"error": "Error al obtener el token", "details": token_data}), 400

@app.route("/callback-notification", methods=["GET", "POST"])
def callback_notification():
    if request.method == "POST":
        # Manejar notificación enviada por Mercado Libre
        notification = request.json  # Accede al cuerpo de la solicitud
        print("Notificación recibida:", notification)
        return jsonify({"status": "ok"}), 200
    elif request.method == "GET":
        # Respuesta para solicitudes GET (pruebas en navegador)
        return jsonify({"message": "Ruta de callback funcionando correctamente"}), 200

@app.route("/get-user-id", methods=["GET"])
def get_user_id():
    """Obtiene el user_id del usuario autenticado"""
    access_token = get_valid_access_token()
    if not access_token:
        return jsonify({"error": "No se pudo obtener un Access Token válido"}), 401

    url = "https://api.mercadolibre.com/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Error al obtener el user_id", "details": response.json()}), response.status_code

    user_data = response.json()
    return jsonify({"user_id": user_data["id"]})

@app.route("/get-products", methods=["GET"])
def get_products():
    """Obtiene 10 productos del vendedor"""
    access_token = get_valid_access_token()
    if not access_token:
        return jsonify({"error": "No se pudo obtener un Access Token válido"}), 401

    # Obtener el user_id
    user_url = "https://api.mercadolibre.com/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(user_url, headers=headers)
    if user_response.status_code != 200:
        return jsonify({"error": "Error al obtener el user_id", "details": user_response.json()}), user_response.status_code

    user_id = user_response.json().get("id")
    if not user_id:
        return jsonify({"error": "No se pudo obtener el user_id"}), 400

    # Obtener productos activos (o pausados según sea necesario)
    items_url = f"https://api.mercadolibre.com/users/{user_id}/items/search"
    params = {"status": "active", "limit": 10}
    items_response = requests.get(items_url, headers=headers, params=params)
    if items_response.status_code != 200:
        return jsonify({"error": "Error al consultar productos", "details": items_response.json()}), items_response.status_code

    # Devuelve los IDs de los productos
    products = items_response.json().get("results", [])
    return jsonify({"products": products})

if __name__ == "__main__":
    app.run(debug=True)