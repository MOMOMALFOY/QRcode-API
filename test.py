import httpx
import os
import time
from datetime import datetime, timedelta

def check_image_file(filename, min_size=1000):
    if not os.path.exists(filename):
        print(f"[ERREUR] {filename} n'a pas été créé.")
        return False
    size = os.path.getsize(filename)
    if size < min_size:
        print(f"[ERREUR] {filename} est trop petit ({size} octets) : image probablement invalide.")
        return False
    print(f"[OK] {filename} généré ({size} octets)")
    return True

def test_upload_image():
    if not os.path.exists("test_logo.png"):
        print("[INFO] test_logo.png absent, upload non testé.")
        return
    with open("test_logo.png", "rb") as f:
        files = {"file": ("test_logo.png", f, "image/png")}
        r = httpx.post("http://127.0.0.1:8000/upload-image", files=files)
        print("upload_image:", r.status_code, r.json())

def test_create_custom_qr():
    data = {
        "data": "https://example.com",
        "body_color": "#FF0000",
        "bg_color": "#FFFFFF",
        "size": 400,
        "file": "png"
    }
    files = {}
    if os.path.exists("test_logo.png"):
        files["logo"] = ("test_logo.png", open("test_logo.png", "rb"), "image/png")
    r = httpx.post("http://127.0.0.1:8000/create-custom-qr", data=data, files=files)
    print("create_custom_qr:", r.status_code, r.headers.get("content-type"))
    with open("qr_custom.png", "wb") as f:
        f.write(r.content)
    check_image_file("qr_custom.png")

def test_get_custom_qr():
    params = {
        "data": "https://example.com",
        "body_color": "#0000FF",
        "bg_color": "#FFFFFF",
        "size": 300,
        "file": "png"
    }
    r = httpx.get("http://127.0.0.1:8000/create-custom-qr", params=params)
    print("get_custom_qr:", r.status_code, r.headers.get("content-type"))
    with open("qr_custom_get.png", "wb") as f:
        f.write(r.content)
    check_image_file("qr_custom_get.png")

def test_create_transparent_qr():
    data = {
        "data": "https://transparent.com",
        "size": 400,
        "file": "png"
    }
    r = httpx.post("http://127.0.0.1:8000/create-transparent-qr", data=data)
    print("create_transparent_qr:", r.status_code, r.headers.get("content-type"))
    with open("qr_transparent.png", "wb") as f:
        f.write(r.content)
    check_image_file("qr_transparent.png")

def test_get_transparent_qr():
    params = {
        "data": "https://transparent.com",
        "size": 300,
        "file": "png"
    }
    r = httpx.get("http://127.0.0.1:8000/create-transparent-qr", params=params)
    print("get_transparent_qr:", r.status_code, r.headers.get("content-type"))
    with open("qr_transparent_get.png", "wb") as f:
        f.write(r.content)
    check_image_file("qr_transparent_get.png")

def test_advanced_qr():
    data = {
        "data": "https://example.com",
        "module_style": "circle",
        "gradient_type": "radial",
        "start_color": "#FF0000",
        "end_color": "#0000FF",
        "caption": "Mon QR personnalisé",
        "size": 400,
        "file": "png"
    }
    r = httpx.post("http://127.0.0.1:8000/create-advanced-qr", data=data)
    print("create_advanced_qr:", r.status_code, r.headers.get("content-type"))
    with open("qr_advanced.png", "wb") as f:
        f.write(r.content)
    check_image_file("qr_advanced.png")
    # Test base64
    data["as_base64"] = True
    r = httpx.post("http://127.0.0.1:8000/create-advanced-qr", data=data)
    if r.status_code == 200 and "base64" in r.json():
        print("[OK] Réponse base64 reçue (longueur:", len(r.json()["base64"]), ")")
    else:
        print("[ERREUR] Pas de base64 dans la réponse advanced QR.")

def test_advanced_qr_svg():
    data = {
        "data": "https://example.com",
        "module_style": "vertical",
        "gradient_type": "horizontal",
        "start_color": "#00FF00",
        "end_color": "#0000FF",
        "size": 400,
        "file": "svg"
    }
    r = httpx.post("http://127.0.0.1:8000/create-advanced-qr", data=data)
    print("create_advanced_qr SVG:", r.status_code, r.headers.get("content-type"))
    with open("qr_advanced.svg", "wb") as f:
        f.write(r.content)
    check_image_file("qr_advanced.svg", min_size=200)

def test_dynamic_qr():
    # Création d'un QR dynamique qui expire dans 1 minute
    data = {
        "target_url": "https://openai.com",
        "expire_in_days": 0,  # 0 = aujourd'hui
        "module_style": "rounded",
        "gradient_type": "vertical",
        "start_color": "#000000",
        "end_color": "#00FF00",
        "size": 400,
        "file": "png"
    }
    r = httpx.post("http://127.0.0.1:8000/create-dynamic-qr", data=data)
    print("create_dynamic_qr:", r.status_code, r.headers.get("content-type"))
    with open("qr_dynamic.png", "wb") as f:
        f.write(r.content)
    check_image_file("qr_dynamic.png")
    # Récupérer l'ID du QR (depuis la redirection dans le QR, à parser manuellement si besoin)
    # Pour le test, on va simuler une récupération d'ID
    # Ici, on suppose que l'API expose l'ID dans la réponse (à améliorer côté API si besoin)
    # Pour le test, on va ajouter un endpoint temporaire pour lister les QR dynamiques si besoin

def test_update_and_redirect_dynamic_qr():
    # Pour ce test, il faut connaître un qr_id existant
    # On va simuler la création et l'utilisation
    # Ajout d'un endpoint temporaire pour lister les QR dynamiques serait utile pour un vrai test automatisé
    print("[INFO] Test de redirection et update à faire manuellement ou avec endpoint de debug.")

if __name__ == "__main__":
    # Optionnel : place un petit logo PNG nommé test_logo.png dans le dossier pour tester l'upload et le logo QR
    if os.path.exists("test_logo.png"):
        test_upload_image()
    test_create_custom_qr()
    test_get_custom_qr()
    test_create_transparent_qr()
    test_get_transparent_qr()
    test_advanced_qr()
    test_advanced_qr_svg()
    test_dynamic_qr()
    test_update_and_redirect_dynamic_qr() 