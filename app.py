from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance
import numpy as np
import cv2
from rembg import remove
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

PAPER_SIZES = {
    "4x6": (4, 6),
    "5x7": (5, 7),
    "8x10": (8, 10),
    "A4": (8.27, 11.69)
}

DPI = 300

def enhance_image(img):
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    img = ImageEnhance.Contrast(img).enhance(1.3)
    img = ImageEnhance.Brightness(img).enhance(1.1)
    return img

def color_grade(img, mode):
    if mode == "warm":
        r, g, b = img.split()
        r = r.point(lambda i: i * 1.1)
        return Image.merge("RGB", (r, g, b))
    elif mode == "cool":
        r, g, b = img.split()
        b = b.point(lambda i: i * 1.1)
        return Image.merge("RGB", (r, g, b))
    return img

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        bg_color = request.form["bg"]
        paper = request.form["paper"]
        copies = int(request.form["copies"])
        grade = request.form["grade"]

        img = Image.open(file).convert("RGBA")

        img = remove(img)

        bg = Image.new("RGBA", img.size, bg_color)
        img = Image.alpha_composite(bg, img).convert("RGB")

        img = enhance_image(img)
        img = color_grade(img, grade)

        w_in, h_in = PAPER_SIZES[paper]
        w_px = int(w_in * DPI)
        h_px = int(h_in * DPI)

        canvas = Image.new("RGB", (w_px, h_px), "white")
        photo = img.resize((int(w_px/4), int(h_px/4)))

        x, y = 0, 0
        for i in range(copies):
            canvas.paste(photo, (x, y))
            x += photo.width
            if x + photo.width > w_px:
                x = 0
                y += photo.height

        output = io.BytesIO()
        canvas.save(output, format="JPEG")
        output.seek(0)

        return send_file(output, mimetype='image/jpeg')

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
