# The Pitch Visualizer 🎬

> From words to storyboard — AI-generated visuals for your startup pitch.

## What it does

Paste your startup pitch narrative. The engine:
1. **Segments** the narrative into 3–5 logical scenes
2. **Engineers enhanced prompts** with style modifiers (cinematic, watercolor, sketch, oil)
3. **Generates images** using the **Pollinations.ai** free API — no API key required
4. **Returns** a full storyboard with scene text + generated image for each scene

## Image Styles

| Style      | Description |
|------------|-------------|
| Cinematic  | High-tech, dramatic lighting, 8K, hyper-realistic |
| Watercolor | Soft hand-painted, pastel, storybook feel |
| Sketch     | Charcoal/pencil, minimalist, professional storyboard |
| Oil        | Rich pigments, classical masterpiece, textured canvas |

## Running Locally

```bash
# From the drwix-assignment root
source venv/bin/activate
cd pitch-visualizer
python app.py
# → http://localhost:8001
```

## API

```
POST /generate-storyboard
Content-Type: multipart/form-data
Body: text=<narrative>&style=cinematic

Response:
{
  "style": "cinematic",
  "storyboard": [
    {
      "scene_number": 1,
      "text": "We are building an AI-powered platform...",
      "prompt": "<enhanced prompt>",
      "image_url": "https://image.pollinations.ai/prompt/..."
    },
    ...
  ]
}
```

## Free Image API: Pollinations.ai

This app uses [Pollinations.ai](https://pollinations.ai) — a **completely free**, no-signup image generation API.

```
https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed=42&nologo=true
```

- ✅ No API key
- ✅ No rate limits for personal/demo use
- ✅ Powered by open-source models (Flux, SDXL)

## Tech Stack

- **FastAPI** — async web framework
- **Pollinations.ai** — free AI image generation
- **Python 3.14**
