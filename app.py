import os
import re
import urllib.parse
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Initialize FastAPI
app = FastAPI(title="The Pitch Visualizer")

# Setup safe directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates
# Bypassing Starlette's Jinja2Templates due to an 'unhashable dict' bug in certain environments
with open(os.path.join(TEMPLATES_DIR, "index.html"), "r") as f:
    INDEX_HTML = f.read()

# Style Modifiers for "Supercharger" Prompt Engineering
STYLE_MODIFIERS = {
    "cinematic": "Cinematic digital art, high-tech, dramatic lighting, 8k resolution, professional composition, hyper-realistic details, futuristic aesthetic.",
    "watercolor": "Soft watercolor illustration, storybook style, hand-painted, delicate textures, pastel color palette, whimsical and dreamy, artistic paper grain.",
    "sketch": "Minimalist architectural sketch, charcoal and pencil, clean deliberate lines, high-contrast black and white, elegant artistic white space, professional storyboard style.",
    "oil": "Rich oil painting, thick brushstrokes, classical masterpiece style, vibrant pigments, textured canvas, dramatic chiaroscuro lighting, museum quality.",
}

def segment_narrative(text):
    """
    Splits the narrative into logical scenes (3-5 sentences).
    """
    # Simple regex-based sentence splitter
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    # Ensure at least 3 scenes, but no more than 5 for performance
    if len(sentences) < 3:
        # If too short, but we need 3, we might have to be creative or just return what we have
        return sentences
    return sentences[:5]

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse(content=INDEX_HTML)

@app.post("/generate-storyboard")
async def generate_storyboard(text: str = Form(...), style: str = Form("cinematic")):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Narrative cannot be empty")

    # 1. Narrative Segmentation
    scenes = segment_narrative(text)
    
    # 2. Intelligent Prompt Engineering & Image URL Generation
    storyboard = []
    style_suffix = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["cinematic"])
    
    for i, scene in enumerate(scenes):
        # Enhance prompt
        enhanced_prompt = f"{scene}. {style_suffix}"
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        
        # Use Pollinations.ai for high-quality, free image generation
        # We use a unique seed for each scene to maintain some consistency but ensure variety
        seed = hash(text) + i
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true"
        
        storyboard.append({
            "scene_number": i + 1,
            "text": scene,
            "prompt": enhanced_prompt,
            "image_url": image_url
        })

    return JSONResponse({
        "storyboard": storyboard,
        "style": style
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
