import os
import re
import urllib.parse
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

# Initialize FastAPI
app = FastAPI(title="The Pitch Visualizer")

# Style Modifiers for "Supercharger" Prompt Engineering
STYLE_MODIFIERS = {
    "cinematic": "Cinematic digital art, high-tech, dramatic lighting, 8k resolution, professional composition, hyper-realistic details, futuristic aesthetic.",
    "watercolor": "Soft watercolor illustration, storybook style, hand-painted, delicate textures, pastel color palette, whimsical and dreamy, artistic paper grain.",
    "sketch": "Minimalist architectural sketch, charcoal and pencil, clean deliberate lines, high-contrast black and white, elegant artistic white space, professional storyboard style.",
    "oil": "Rich oil painting, thick brushstrokes, classical masterpiece style, vibrant pigments, textured canvas, dramatic chiaroscuro lighting, museum quality.",
}

# Inline HTML — no filesystem dependency (works on Vercel serverless)
INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Pitch Visualizer | From Words to Storyboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --background: #fcfcfd;
            --surface: #ffffff;
            --surface-low: #f8f9fc;
            --surface-high: #f0f2f7;
            --on-surface: #020617;
            --on-surface-variant: #64748b;
            --primary: #2563eb;
            --primary-container: #dbeafe;
            --font-outfit: 'Outfit', sans-serif;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: var(--background); color: var(--on-surface); font-family: var(--font-outfit); min-height: 100vh; padding: 4rem 2rem; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 5rem; }
        h1 { font-size: 4rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 1rem; color: var(--on-surface); }
        .subtitle { font-size: 1.25rem; color: var(--on-surface-variant); text-transform: uppercase; letter-spacing: 3px; font-weight: 600; }
        .input-card { background: var(--surface); border-radius: 40px; padding: 3rem; box-shadow: 0 40px 100px rgba(0,0,0,0.03); margin-bottom: 4rem; }
        .form-group { margin-bottom: 2rem; }
        label { display: block; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; color: var(--on-surface-variant); }
        textarea { width: 100%; height: 160px; background: var(--surface-low); border: none; border-radius: 24px; padding: 2rem; font-size: 1.2rem; color: var(--on-surface); font-family: var(--font-outfit); resize: none; transition: all 0.3s ease; }
        textarea:focus { outline: none; background: var(--surface-high); box-shadow: 0 0 0 2px var(--primary-container); }
        .select-wrapper { display: flex; gap: 1rem; flex-wrap: wrap; }
        select { padding: 1.2rem 2.5rem; background: var(--surface-low); border: none; border-radius: 100px; font-size: 1rem; font-weight: 600; color: var(--on-surface); cursor: pointer; appearance: none; font-family: var(--font-outfit); transition: all 0.3s ease; }
        #generate-btn { background: var(--on-surface); color: #fff; border: none; padding: 1.2rem 3.5rem; border-radius: 100px; font-size: 1.1rem; font-weight: 700; cursor: pointer; transition: all 0.4s cubic-bezier(0.175,0.885,0.32,1.275); }
        #generate-btn:hover { transform: translateY(-5px); box-shadow: 0 20px 40px rgba(0,0,0,0.2); }
        #generate-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .storyboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2.5rem; margin-top: 4rem; opacity: 0; transform: translateY(30px); transition: all 0.8s ease; }
        .storyboard-grid.visible { opacity: 1; transform: translateY(0); }
        .panel { background: var(--surface); border-radius: 32px; overflow: hidden; box-shadow: 0 25px 60px rgba(0,0,0,0.05); transition: transform 0.4s ease; }
        .panel:hover { transform: scale(1.02); }
        .image-container { width: 100%; aspect-ratio: 1; background: var(--surface-high); position: relative; overflow: hidden; }
        .image-container img { width: 100%; height: 100%; object-fit: cover; display: none; }
        .loader { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); width: 40px; height: 40px; border: 4px solid var(--surface-high); border-top: 4px solid var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: translate(-50%,-50%) rotate(360deg); } }
        .caption { padding: 2.5rem; }
        .scene-tag { display: inline-block; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; color: var(--primary); margin-bottom: 1rem; background: var(--primary-container); padding: 0.4rem 1rem; border-radius: 100px; }
        .scene-text { font-size: 1.1rem; line-height: 1.6; font-weight: 500; }
        .footer { text-align: center; margin-top: 6rem; color: var(--on-surface-variant); font-size: 0.9rem; letter-spacing: 1px; text-transform: uppercase; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <p class="subtitle">Narrative Visualization Engine</p>
            <h1>The Pitch Visualizer</h1>
        </header>
        <main>
            <section class="input-card">
                <div class="form-group">
                    <label for="narrative-input">Your Success Story / Pitch Narrative</label>
                    <textarea id="narrative-input" placeholder="Enter a 3-5 sentence narrative and see it come to life as a visual storyboard..."></textarea>
                </div>
                <div class="select-wrapper">
                    <div style="flex: 1">
                        <label>Visual Style</label>
                        <select id="style-select">
                            <option value="cinematic">Cinematic Digital Art</option>
                            <option value="watercolor">Watercolor Storybook</option>
                            <option value="sketch">Minimalist Sketch</option>
                            <option value="oil">Oil Painting Masterpiece</option>
                        </select>
                    </div>
                    <button id="generate-btn">Generate Storyboard</button>
                </div>
            </section>
            <section class="storyboard-grid" id="storyboard-grid"></section>
        </main>
        <footer class="footer">Built for visual storytellers and sales visionaries</footer>
    </div>
    <script>
        const generateBtn = document.getElementById('generate-btn');
        const narrativeInput = document.getElementById('narrative-input');
        const styleSelect = document.getElementById('style-select');
        const storyboardGrid = document.getElementById('storyboard-grid');

        generateBtn.addEventListener('click', async () => {
            const text = narrativeInput.value.trim();
            if (!text) return;
            generateBtn.disabled = true;
            generateBtn.textContent = 'Engineering Storyboard...';
            storyboardGrid.innerHTML = '';
            storyboardGrid.classList.remove('visible');
            const formData = new FormData();
            formData.append('text', text);
            formData.append('style', styleSelect.value);
            try {
                const response = await fetch('/generate-storyboard', { method: 'POST', body: formData });
                if (!response.ok) throw new Error('Generation failed');
                const data = await response.json();
                data.storyboard.forEach((panel, index) => {
                    const panelEl = document.createElement('div');
                    panelEl.className = 'panel';
                    panelEl.style.animationDelay = `${index * 0.2}s`;
                    panelEl.innerHTML = `
                        <div class="image-container">
                            <div class="loader"></div>
                            <img src="${panel.image_url}" alt="Scene ${panel.scene_number}">
                        </div>
                        <div class="caption">
                            <span class="scene-tag">Scene ${panel.scene_number}</span>
                            <p class="scene-text">${panel.text}</p>
                        </div>`;
                    storyboardGrid.appendChild(panelEl);
                    const img = panelEl.querySelector('img');
                    const loader = panelEl.querySelector('.loader');
                    img.onload = () => { loader.style.display = 'none'; img.style.display = 'block'; };
                });
                storyboardGrid.classList.add('visible');
                generateBtn.textContent = 'Generate Storyboard';
            } catch (error) {
                console.error(error);
                alert('An error occurred during generation.');
                generateBtn.textContent = 'Generate Storyboard';
            } finally {
                generateBtn.disabled = false;
            }
        });
    </script>
</body>
</html>"""


def segment_narrative(text):
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    if len(sentences) < 3:
        return sentences
    return sentences[:5]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse(content=INDEX_HTML)


@app.post("/generate-storyboard")
async def generate_storyboard(text: str = Form(...), style: str = Form("cinematic")):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Narrative cannot be empty")

    scenes = segment_narrative(text)
    storyboard = []
    style_suffix = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["cinematic"])

    for i, scene in enumerate(scenes):
        enhanced_prompt = f"{scene}. {style_suffix}"
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        seed = hash(text) + i
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true"
        storyboard.append({
            "scene_number": i + 1,
            "text": scene,
            "prompt": enhanced_prompt,
            "image_url": image_url
        })

    return JSONResponse({"storyboard": storyboard, "style": style})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
