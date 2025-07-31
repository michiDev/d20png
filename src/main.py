from PIL import Image, ImageDraw, ImageFont
import random
import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI(title="D20 PNG Generator", description="Generate random D20 dice images")

def generate_d20_image():
    """Generate a random D20 dice image and return it as bytes"""
    # Open an existing PNG image
    image = Image.open('d20blank.png')
    image = image.rotate(180)
    
    # Create a new image with white background
    if image.mode in ('RGBA', 'LA'):
        # Create a white background image
        background = Image.new('RGB', image.size, (255, 255, 255))
        # Paste the original image onto the white background
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background
    elif image.mode == 'P':
        # Convert palette mode to RGB with white background
        image = image.convert('RGB')

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Add text to the image
    text = str(random.randint(1, 20))
    font = ImageFont.truetype("arial.ttf", 90)
    img_width, img_height = image.size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (img_width - text_width) // 2
    y = (img_height - text_height) // 2
    position = (x, y-10)
    fill_color = (0, 0, 0)  # Black text (R, G, B)

    draw.text(position, text, fill=fill_color, font=font, stroke_width=3)
    
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "D20 PNG Generator API", 
        "endpoints": {
            "/d20": "Get a random D20 dice image",
            "/docs": "API documentation"
        }
    }

@app.get("/d20")
async def get_d20_image():
    """Generate and return a random D20 dice image"""
    img_buffer = generate_d20_image()
    
    return StreamingResponse(
        io.BytesIO(img_buffer.getvalue()),
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=d20.png"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)