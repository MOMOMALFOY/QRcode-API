from fastapi import FastAPI, UploadFile, File, Form, Query, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, RedirectResponse
from typing import Optional
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, GappedSquareModuleDrawer, CircleModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask, RadialGradiantColorMask, HorizontalGradiantColorMask, VerticalGradiantColorMask
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import uuid
from datetime import datetime, timedelta
from qrcode.image.svg import SvgImage

app = FastAPI(title="QR Code API")

# Stockage en mémoire pour les QR dynamiques
DYNAMIC_QR_DB = {}

# Utilitaires graphiques
MODULE_STYLES = {
    "square": SquareModuleDrawer(),
    "rounded": RoundedModuleDrawer(),
    "gapped": GappedSquareModuleDrawer(),
    "circle": CircleModuleDrawer(),
    "vertical": VerticalBarsDrawer(),
    "horizontal": HorizontalBarsDrawer(),
}

GRADIENTS = {
    "solid": SolidFillColorMask,
    "radial": RadialGradiantColorMask,
    "horizontal": HorizontalGradiantColorMask,
    "vertical": VerticalGradiantColorMask,
}

def hex_to_rgb(hex_color: str, alpha: Optional[int] = None):
    """Convertit une couleur hexadécimale en tuple RGB ou RGBA."""
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    rgb = tuple(int(hex_color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    if alpha is not None:
        return (*rgb, alpha)
    return rgb

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    # Stockage temporaire en mémoire, retourne le contenu binaire
    content = await file.read()
    return {"filename": file.filename, "content": content.hex()}

@app.post("/create-custom-qr")
async def create_custom_qr(
    data: str = Form(...),
    body_color: Optional[str] = Form("#000000"),
    bg_color: Optional[str] = Form("#FFFFFF"),
    size: Optional[int] = Form(600),
    logo: Optional[UploadFile] = File(None),
    file: Optional[str] = Form("png")
):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    front_rgb = hex_to_rgb(body_color)
    back_rgb = hex_to_rgb(bg_color)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(front_color=front_rgb, back_color=back_rgb)
    ).convert("RGBA")
    # Redimensionnement
    img = img.resize((size, size))
    # Ajout du logo si fourni
    if logo:
        logo_bytes = await logo.read()
        logo_img = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
        # Redimensionne le logo
        logo_size = int(size * 0.2)
        logo_img = logo_img.resize((logo_size, logo_size))
        pos = ((img.size[0] - logo_size) // 2, (img.size[1] - logo_size) // 2)
        img.paste(logo_img, pos, mask=logo_img)
    buf = io.BytesIO()
    img.save(buf, format=file.upper())
    buf.seek(0)
    return StreamingResponse(buf, media_type=f"image/{file}")

@app.get("/create-custom-qr")
async def get_custom_qr(
    data: str = Query(...),
    body_color: Optional[str] = Query("#000000"),
    bg_color: Optional[str] = Query("#FFFFFF"),
    size: Optional[int] = Query(600),
    file: Optional[str] = Query("png")
):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    front_rgb = hex_to_rgb(body_color)
    back_rgb = hex_to_rgb(bg_color)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(front_color=front_rgb, back_color=back_rgb)
    ).convert("RGBA")
    img = img.resize((size, size))
    buf = io.BytesIO()
    img.save(buf, format=file.upper())
    buf.seek(0)
    return StreamingResponse(buf, media_type=f"image/{file}")

@app.post("/create-transparent-qr")
async def create_transparent_qr(
    data: str = Form(...),
    size: Optional[int] = Form(400),
    file: Optional[str] = Form("png")
):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    front_rgb = (0, 0, 0)
    back_rgb = (255, 255, 255)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=GappedSquareModuleDrawer(),
        color_mask=SolidFillColorMask(front_color=front_rgb, back_color=back_rgb)
    ).convert("RGBA")
    img = img.resize((size, size))
    datas = img.getdata()
    newData = []
    for item in datas:
        # Si le pixel est blanc, on le rend transparent
        if item[0] > 250 and item[1] > 250 and item[2] > 250:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    buf = io.BytesIO()
    img.save(buf, format=file.upper())
    buf.seek(0)
    return StreamingResponse(buf, media_type=f"image/{file}")

@app.get("/create-transparent-qr")
async def get_transparent_qr(
    data: str = Query(...),
    size: Optional[int] = Query(400),
    file: Optional[str] = Query("png")
):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    front_rgb = (0, 0, 0)
    back_rgb = (255, 255, 255)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=GappedSquareModuleDrawer(),
        color_mask=SolidFillColorMask(front_color=front_rgb, back_color=back_rgb)
    ).convert("RGBA")
    img = img.resize((size, size))
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] > 250 and item[1] > 250 and item[2] > 250:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    buf = io.BytesIO()
    img.save(buf, format=file.upper())
    buf.seek(0)
    return StreamingResponse(buf, media_type=f"image/{file}")

def add_caption(img, caption, size):
    draw = ImageDraw.Draw(img)
    font_size = int(size * 0.06)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), caption, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    new_img = Image.new("RGBA", (img.width, img.height + h + 10), (255,255,255,0))
    new_img.paste(img, (0,0))
    draw = ImageDraw.Draw(new_img)
    draw.text(((img.width-w)//2, img.height+5), caption, fill=(0,0,0,255), font=font)
    return new_img

@app.post("/create-advanced-qr")
async def create_advanced_qr(
    data: str = Form(...),
    module_style: str = Form("square"),
    gradient_type: str = Form("solid"),
    start_color: str = Form("#000000"),
    end_color: str = Form("#FFFFFF"),
    eye_color: str = Form("#000000"),
    caption: Optional[str] = Form(None),
    size: int = Form(600),
    file: str = Form("png"),
    as_base64: bool = Form(False)
):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    module_drawer = MODULE_STYLES.get(module_style, SquareModuleDrawer())
    color_mask_cls = GRADIENTS.get(gradient_type, SolidFillColorMask)
    front = hex_to_rgb(start_color)
    back = hex_to_rgb(end_color)
    if gradient_type == "solid":
        color_mask = color_mask_cls(front_color=front, back_color=back)
    elif gradient_type == "radial":
        color_mask = color_mask_cls()
        color_mask.center_color = front
        color_mask.edge_color = back
    elif gradient_type == "horizontal":
        color_mask = color_mask_cls()
        color_mask.left_color = front
        color_mask.right_color = back
    elif gradient_type == "vertical":
        color_mask = color_mask_cls()
        color_mask.top_color = front
        color_mask.bottom_color = back
    else:
        color_mask = SolidFillColorMask(front_color=front, back_color=back)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=module_drawer,
        color_mask=color_mask
    ).convert("RGBA")
    img = img.resize((size, size))
    if caption:
        img = add_caption(img, caption, size)
    buf = io.BytesIO()
    if file == "svg":
        qr_svg = qrcode.make(data, image_factory=SvgImage)
        qr_svg.save(buf)
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/svg+xml")
    elif file == "pdf":
        img.save(buf, format="PDF")
        buf.seek(0)
        return StreamingResponse(buf, media_type="application/pdf")
    elif file == "webp":
        img.save(buf, format="WEBP")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/webp")
    elif as_base64:
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        return {"base64": b64}
    else:
        img.save(buf, format=file.upper())
        buf.seek(0)
        return StreamingResponse(buf, media_type=f"image/{file}")

@app.post("/create-dynamic-qr")
async def create_dynamic_qr(
    target_url: str = Form(...),
    expire_in_days: int = Form(7),
    module_style: str = Form("square"),
    gradient_type: str = Form("solid"),
    start_color: str = Form("#000000"),
    end_color: str = Form("#FFFFFF"),
    size: int = Form(600),
    file: str = Form("png")
):
    qr_id = str(uuid.uuid4())
    expire_at = datetime.utcnow() + timedelta(days=expire_in_days)
    DYNAMIC_QR_DB[qr_id] = {"target_url": target_url, "expire_at": expire_at}
    # Le QR code pointe vers /redirect/{qr_id}
    redirect_url = f"http://127.0.0.1:8000/redirect/{qr_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(redirect_url)
    qr.make(fit=True)
    module_drawer = MODULE_STYLES.get(module_style, SquareModuleDrawer())
    color_mask_cls = GRADIENTS.get(gradient_type, SolidFillColorMask)
    front = hex_to_rgb(start_color)
    back = hex_to_rgb(end_color)
    if gradient_type == "solid":
        color_mask = color_mask_cls(front_color=front, back_color=back)
    elif gradient_type == "radial":
        color_mask = color_mask_cls()
        color_mask.center_color = front
        color_mask.edge_color = back
    elif gradient_type == "horizontal":
        color_mask = color_mask_cls()
        color_mask.left_color = front
        color_mask.right_color = back
    elif gradient_type == "vertical":
        color_mask = color_mask_cls()
        color_mask.top_color = front
        color_mask.bottom_color = back
    else:
        color_mask = SolidFillColorMask(front_color=front, back_color=back)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=module_drawer,
        color_mask=color_mask
    ).convert("RGBA")
    img = img.resize((size, size))
    buf = io.BytesIO()
    img.save(buf, format=file.upper())
    buf.seek(0)
    return StreamingResponse(buf, media_type=f"image/{file}")

@app.get("/redirect/{qr_id}")
async def redirect_dynamic_qr(qr_id: str):
    qr_info = DYNAMIC_QR_DB.get(qr_id)
    if not qr_info:
        return JSONResponse({"error": "QR code inconnu ou expiré."}, status_code=404)
    if datetime.utcnow() > qr_info["expire_at"]:
        return JSONResponse({"error": "Ce QR code a expiré."}, status_code=410)
    return RedirectResponse(qr_info["target_url"])

@app.post("/update-dynamic-qr")
async def update_dynamic_qr(qr_id: str = Form(...), new_url: str = Form(...), extend_days: int = Form(0)):
    qr_info = DYNAMIC_QR_DB.get(qr_id)
    if not qr_info:
        return JSONResponse({"error": "QR code inconnu."}, status_code=404)
    qr_info["target_url"] = new_url
    if extend_days > 0:
        qr_info["expire_at"] = qr_info["expire_at"] + timedelta(days=extend_days)
    return {"message": "QR code dynamique mis à jour.", "expire_at": qr_info["expire_at"].isoformat()}

@app.middleware("http")
async def check_rapidapi_host(request: Request, call_next):
    # Autorise /ping et / même sans header pour le healthcheck
    if request.url.path not in ["/ping", "/"]:
        if not request.headers.get("x-rapidapi-host"):
            return JSONResponse({"error": "Cette API n'est accessible que via RapidAPI."}, status_code=403)
    return await call_next(request)

@app.get("/", tags=["Accueil"])
async def accueil():
    return {
        "message": "Bienvenue sur l'API QR Code avancée ! Utilisez cette API via RapidAPI pour générer des QR codes personnalisés, dynamiques, transparents, etc. Toutes les requêtes doivent passer par RapidAPI (en-tête x-rapidapi-host obligatoire). Consultez la documentation sur RapidAPI pour les exemples d'utilisation."
    }

@app.get("/ping", tags=["Healthcheck"])
async def ping():
    """Endpoint de healthcheck pour RapidAPI."""
    return {"status": "ok"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port) 