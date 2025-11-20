import httpx

response = httpx.get("http://localhost:8001/docs")
print(response.status_code)
print(response.text[:500])  # primeros 500 caracteres
