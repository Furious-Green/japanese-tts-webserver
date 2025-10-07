import torch
import torchaudio
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer, AutoModelForCausalLM
import soundfile as sf
from rubyinserter import add_ruby
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse
import os
import tempfile
import uuid

try:
    from canary_tts.xcodec2.modeling_xcodec2 import XCodec2Model
    CANARY_AVAILABLE = True
except ImportError:
    CANARY_AVAILABLE = False
    print("Warning: canary_tts not available.")

try:
    import requests
    FISH_SPEECH_AVAILABLE = True
except ImportError:
    FISH_SPEECH_AVAILABLE = False
    print("Warning: fish_speech not available.")

app = FastAPI()

device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Load Parler TTS models
parler_model = ParlerTTSForConditionalGeneration.from_pretrained(
    "2121-8/japanese-parler-tts-mini").to(device)
parler_prompt_tokenizer = AutoTokenizer.from_pretrained(
    "2121-8/japanese-parler-tts-mini", subfolder="prompt_tokenizer")
parler_description_tokenizer = AutoTokenizer.from_pretrained(
    "2121-8/japanese-parler-tts-mini", subfolder="description_tokenizer")

# Load Canary TTS models (if available)
canary_model = None
canary_tokenizer = None
canary_codec = None

if CANARY_AVAILABLE:
    try:
        canary_tokenizer = AutoTokenizer.from_pretrained(
            "2121-8/canary-tts-0.5b")
        canary_model = AutoModelForCausalLM.from_pretrained(
            "2121-8/canary-tts-0.5b", device_map="auto",
            torch_dtype=torch.bfloat16)
        canary_codec = XCodec2Model.from_pretrained("HKUSTAudio/xcodec2")
        print("Canary TTS models loaded successfully")
    except Exception as e:
        print(f"Failed to load Canary TTS models: {e}")
        CANARY_AVAILABLE = False

# Fish Speech API configuration (assuming local API server)
FISH_SPEECH_API_URL = "http://localhost:8080"


def check_fish_speech_api():
    """Check if Fish Speech API server is running"""
    if not FISH_SPEECH_AVAILABLE:
        return False
    try:
        response = requests.get(f"{FISH_SPEECH_API_URL}/", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


if FISH_SPEECH_AVAILABLE:
    FISH_SPEECH_API_RUNNING = check_fish_speech_api()
else:
    FISH_SPEECH_API_RUNNING = False
if FISH_SPEECH_AVAILABLE and FISH_SPEECH_API_RUNNING:
    print("Fish Speech API server detected")
elif FISH_SPEECH_AVAILABLE:
    print("Fish Speech dependencies available but API server not running")


@app.get("/", response_class=HTMLResponse)
async def home():
    if CANARY_AVAILABLE:
        canary_option = '<option value="canary">Canary TTS</option>'
    else:
        canary_option = '<option value="canary" disabled>Canary TTS (Not Available)</option>'
    if (FISH_SPEECH_AVAILABLE and FISH_SPEECH_API_RUNNING):
        fish_option = '<option value="fish">Fish Speech</option>'
    else:
        fish_option = '<option value="fish" disabled>Fish Speech (Not Available)</option>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Japanese TTS</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            textarea {{ width: 100%; height: 100px; margin: 10px 0; }}
            select {{ width: 100%; padding: 8px; margin: 10px 0; }}
            input[type="submit"] {{ background: #007cba; color: white; padding: 10px 20px; border: none; cursor: pointer; }}
            input[type="submit"]:hover {{ background: #005a8a; }}
            audio {{ width: 100%; margin: 20px 0; }}
            .form-group {{ margin: 15px 0; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            .model-info {{ background: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 4px; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>Japanese Text-to-Speech</h1>
        <form action="/generate" method="post">
            <div class="form-group">
                <label for="model">TTS Model:</label>
                <select name="model" id="model" onchange="updateDescription()">
                    <option value="parler">Parler TTS</option>
                    {canary_option}
                    {fish_option}
                </select>
                <div class="model-info" id="model-info">
                    Parler TTS: Uses separate voice description for fine-grained control over voice characteristics.
                </div>
            </div>
            <div class="form-group">
                <label for="prompt">Japanese Text:</label>
                <textarea name="prompt" id="prompt" placeholder="Enter Japanese text here..." required>こんにちは、今日はどのようにお過ごしですか？</textarea>
            </div>
            <div class="form-group">
                <label for="description">Voice Description:</label>
                <textarea name="description" id="description" placeholder="Describe the voice characteristics...">A female speaker with a slightly high-pitched voice delivers her words at a moderate speed with a quite monotone tone in a confined environment, resulting in a quite clear audio recording.</textarea>
            </div>
            <input type="submit" value="Generate Speech">
        </form>

        <script>
        function updateDescription() {{
            const model = document.getElementById('model').value;
            const info = document.getElementById('model-info');
            const description = document.getElementById('description');

            if (model === 'parler') {{
                info.innerHTML = 'Parler TTS: Uses separate voice description for fine-grained control over voice characteristics.';
                description.placeholder = 'Describe the voice characteristics...';
                description.value = 'A female speaker with a slightly high-pitched voice delivers her words at a moderate speed with a quite monotone tone in a confined environment, resulting in a quite clear audio recording.';
            }} else if (model === 'canary') {{
                info.innerHTML = 'Canary TTS: Uses system message format for voice description.';
                description.placeholder = 'Describe the voice characteristics (will be used as system message)...';
                description.value = 'A man voice, with a very hight pitch, speaks in a monotone manner. The recording quality is very noises and close-sounding, indicating a good or excellent audio capture.';
            }} else if (model === 'fish') {{
                info.innerHTML = 'Fish Speech: Supports emotion markers like (angry), (sad), (excited). Add reference audio description for voice cloning.';
                description.placeholder = 'Reference audio description or voice characteristics...';
                description.value = 'A clear female voice with natural intonation. You can add emotion markers like (excited) or (sad) in your text.';
            }}
        }}
        </script>
    </body>
    </html>
    """


@app.post("/generate")
async def generate_speech(prompt: str = Form(...), description: str = Form(...), model: str = Form("parler")):
    prompt_with_ruby = add_ruby(prompt)
    filename = f"tts_{uuid.uuid4().hex}.wav"
    filepath = os.path.join(tempfile.gettempdir(), filename)

    try:
        if model == "parler":
            # Parler TTS generation
            input_ids = parler_description_tokenizer(
                description, return_tensors="pt").input_ids.to(device)
            prompt_input_ids = parler_prompt_tokenizer(
                prompt_with_ruby, return_tensors="pt").input_ids.to(device)

            generation = parler_model.generate(
                input_ids=input_ids, prompt_input_ids=prompt_input_ids)
            audio_arr = generation.cpu().numpy().squeeze()
            sf.write(filepath, audio_arr, parler_model.config.sampling_rate)

        elif model == "canary" and CANARY_AVAILABLE:
            # Canary TTS generation
            chat = [
                {"role": "system", "content": description},
                {"role": "user", "content": prompt_with_ruby}
            ]
            tokenized_input = canary_tokenizer.apply_chat_template(
                chat, add_generation_prompt=True, tokenize=True,
                return_tensors="pt").to(canary_model.device)

            with torch.no_grad():
                output = canary_model.generate(
                    tokenized_input,
                    max_new_tokens=256,
                    top_p=0.95,
                    temperature=0.7,
                    repetition_penalty=1.05,
                )[0]

            audio_tokens = output[len(tokenized_input[0]):]
            output_audios = canary_codec.decode_code(
                audio_tokens.unsqueeze(0).unsqueeze(0).cpu())
            torchaudio.save(
                filepath, src=output_audios[0].cpu(), sample_rate=16000)

        elif model == "fish" and FISH_SPEECH_API_RUNNING:
            # Fish Speech API generation
            api_data = {
                "text": prompt_with_ruby,
                "reference_text": description,
                "reference_audio": None,  # Could be enhanced to support reference audio upload
                "max_new_tokens": 256,
                "top_p": 0.95,
                "temperature": 0.7,
                "repetition_penalty": 1.05
            }

            response = requests.post(
                f"{FISH_SPEECH_API_URL}/v1/tts", json=api_data, timeout=60)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
            else:
                raise ValueError(f"Fish Speech API error: {response.status_code} - {response.text}")

        else:
            raise ValueError(f"Model '{model}' not available or not supported")

    except Exception as e:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .error {{ color: red; background: #ffe6e6; padding: 15px; border-radius: 4px; }}
                .back-link {{ margin: 20px 0; }}
                .back-link a {{ text-decoration: none; background: #007cba; color: white; padding: 10px 20px; }}
            </style>
        </head>
        <body>
            <h1>Error</h1>
            <div class="error">
                <strong>Error generating speech:</strong> {str(e)}
            </div>
            <div class="back-link">
                <a href="/">Try Again</a>
            </div>
        </body>
        </html>
        """)

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Generated Speech</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            audio {{ width: 100%; margin: 20px 0; }}
            .back-link {{ margin: 20px 0; }}
            .back-link a {{ text-decoration: none; background: #007cba; color: white; padding: 10px 20px; }}
            .back-link a:hover {{ background: #005a8a; }}
            .info {{ background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <h1>Generated Speech</h1>
        <div class="info">
            <p><strong>Model:</strong> {model.title()}</p>
            <p><strong>Text:</strong> {prompt}</p>
            <p><strong>Description:</strong> {description}</p>
        </div>
        <audio controls>
            <source src="/audio/{filename}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
        <div class="back-link">
            <a href="/">Generate Another</a>
        </div>
    </body>
    </html>
    """)


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    filepath = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="audio/wav")
    return {"error": "File not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
