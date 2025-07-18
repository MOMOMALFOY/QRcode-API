QR Code API
===========

Easily generate fully customizable QR codes via GET or POST requests.
Supports colors, gradients, module styles, transparent background, captions, and logo embedding (by URL or file upload).

---

Endpoints
---------

1. GET /generate-qr
-------------------
Generate a QR code with all options via query parameters.

Parameters (query):
- data (string, required): Text or URL to encode
- file (string): Output format: png, svg, pdf, webp (default: png)
- size (integer): Size in pixels (default: 400)
- body_color (string): QR color (hex, default: #000000)
- bg_color (string): Background color (hex, default: #FFFFFF)
- transparent (boolean): Transparent background (default: false)
- module_style (string): square, rounded, gapped, circle, vertical, horizontal (default: square)
- gradient_type (string): solid, radial, horizontal, vertical (default: solid)
- start_color (string): Gradient start color (hex, default: #000000)
- end_color (string): Gradient end color (hex, default: #FFFFFF)
- caption (string): Optional text below the QR code
- logo_url (string): URL of a logo image to embed

Response: QR code image in the requested format.

---

2. POST /generate-qr
--------------------
Generate a QR code with all options via form-data.
You can either provide a logo URL (logo_url) or upload a logo file (logo).

Parameters (form-data):
- data (string, required): Text or URL to encode
- file (string): Output format: png, svg, pdf, webp (default: png)
- size (integer): Size in pixels (default: 400)
- body_color (string): QR color (hex, default: #000000)
- bg_color (string): Background color (hex, default: #FFFFFF)
- transparent (boolean): Transparent background (default: false)
- module_style (string): square, rounded, gapped, circle, vertical, horizontal (default: square)
- gradient_type (string): solid, radial, horizontal, vertical (default: solid)
- start_color (string): Gradient start color (hex, default: #000000)
- end_color (string): Gradient end color (hex, default: #FFFFFF)
- caption (string): Optional text below the QR code
- logo_url (string): URL of a logo image to embed
- logo (file): Image file to embed as logo (centered). If both logo_url and logo are provided, the uploaded file is used.

How to add a logo:
- By URL: Set the logo_url parameter to the image URL.
- By file upload: Use the logo field to upload an image file (PNG, JPG, etc.).
- If both are provided, the uploaded file is used.

Response: QR code image in the requested format.

---

Example Usage
-------------
GET example:
  /generate-qr?data=https://example.com&size=400&body_color=%23000000&logo_url=https://site.com/logo.png

POST example (with file upload):
  Use multipart/form-data
  Fields: data, size, logo (file)

---

Notes
-----
- All parameters are optional except data.
- The QR code will work even without a logo or caption.
- For transparent background, set transparent=true and use PNG or WebP format. 