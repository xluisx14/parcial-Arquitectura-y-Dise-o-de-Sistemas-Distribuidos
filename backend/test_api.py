import requests
from pprint import pprint

API_URL = "http://localhost:8001"
TEST_USER = {"username": "admin", "password": "admin123"}

def test_health():
    try:
        response = requests.get(f"{API_URL}/health")
        print("=== Health Check ===")
        pprint(response.json())
    except Exception as e:
        print("Error al consultar /health:", e)

def test_login():
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        print("=== Login ===")
        pprint(response.json())
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception as e:
        print("Error al hacer login:", e)
    return None

def test_protected_route(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/users/me", headers=headers)
        print("=== Protected Route (/users/me) ===")
        pprint(response.json())
    except Exception as e:
        print("Error al acceder a ruta protegida:", e)

def main():
    # Aquí asumimos que ya creaste el usuario admin directamente en la DB
    test_health()
    token = test_login()
    if token:
        test_protected_route(token)
    else:
        print("No se pudo obtener token. Asegúrate de que exista un usuario en la BD.")

if __name__ == "__main__":
    main()