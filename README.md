# Japanese TTS Web Server

A FastAPI-based web server for Japanese Text-to-Speech synthesis supporting multiple TTS models.

## Features

- **Dual Model Support**: Choose between Parler TTS and Canary TTS models
- **Web Interface**: Clean, user-friendly web interface for text input and audio playback
- **Japanese Text Processing**: Automatic ruby insertion for better pronunciation
- **Real-time Generation**: Generate and play audio directly in the browser
- **Model Comparison**: Easy switching between different TTS models

## Supported Models

### Parler TTS
- Model: `2121-8/japanese-parler-tts-mini`
- Uses separate voice description for fine-grained control
- Good for detailed voice characteristic specification

### Canary TTS
- Model: `2121-8/canary-tts-0.5b`
- Uses chat template format with system/user messages
- Advanced conversational AI-based approach

### Fish Speech
- Model: OpenAudio S1 (via API server)
- Supports emotion markers: `(angry)`, `(sad)`, `(excited)`, `(surprised)`, etc.
- Special markers: `(laughing)`, `(whispering)`, `(sighing)`, etc.
- Zero-shot voice cloning with reference audio
- Requires separate Fish Speech API server to be running

## Requirements

- Python 3.10+
- CUDA-compatible GPU (recommended)
- UV package manager

### System Requirements

**GPU/VRAM Requirements (recommended):**
- **Parler TTS (Mini)**: ~2-4 GB VRAM
- **Canary TTS (0.5B)**: ~4-6 GB VRAM
- **Fish Speech (S1-mini)**: ~4 GB VRAM minimum, 12 GB VRAM recommended for optimal performance
- **Total (all models)**: 12-16 GB VRAM recommended if loading multiple models

**CPU-only mode:** All models can run on CPU but will be significantly slower

**Disk Space:**
- **Parler TTS**: ~1-2 GB
- **Canary TTS**: ~2-3 GB
- **Fish Speech**: ~1 GB (S1-mini) or ~8 GB (S1 full)
- **Total**: ~5-10 GB minimum for model downloads and cache

**Initial Setup:** First run will download models from Hugging Face, which may take 10-30 minutes depending on your internet connection.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Furious-Green/japanese-tts-webserver.git
cd japanese-tts-webserver
```

2. Install dependencies using UV:
```bash
uv sync
```

3. Install additional dependencies (optional):
```bash
# For Canary TTS - install canary-tts manually if needed
# For Fish Speech - requires separate installation and API server setup:
# Follow instructions at: https://github.com/fishaudio/fish-speech
# System dependencies: apt install portaudio19-dev libsox-dev ffmpeg
```

## Usage

1. Start the server:
```bash
# Option 1: Using the main script
uv run python main.py

# Option 2: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Open your browser and navigate to `http://localhost:8000`

3. Select your preferred TTS model from the dropdown menu

4. Enter Japanese text in the text area

5. Customize the voice description based on the selected model

6. Click "Generate Speech" to create and play the audio

### Fish Speech Setup (Optional)

To use Fish Speech, you need to run a separate API server:

1. Clone the Fish Speech repository and set it up as mentioned in its README
2. Start the API server:
```bash
python -m tools.api_server --listen 0.0.0.0:8080 \
  --llama-checkpoint-path "checkpoints/openaudio-s1-mini" \
  --decoder-checkpoint-path "checkpoints/openaudio-s1-mini/codec.pth" \
  --decoder-config-name modded_dac_vq
```
3. The web interface will automatically detect the running API server

### Emotion Markers (Fish Speech)

Fish Speech supports various emotion and special markers:

**Emotions**: `(angry)`, `(sad)`, `(excited)`, `(surprised)`, `(satisfied)`, `(delighted)`, `(scared)`, `(worried)`, `(upset)`, `(nervous)`, `(frustrated)`, `(depressed)`, `(empathetic)`, `(embarrassed)`, `(disgusted)`, `(moved)`, `(proud)`, `(relaxed)`, `(grateful)`, `(confident)`, `(interested)`, `(curious)`, `(confused)`, `(joyful)`, etc.

**Special Effects**: `(laughing)`, `(chuckling)`, `(sobbing)`, `(crying loudly)`, `(sighing)`, `(panting)`, `(groaning)`, `(whispering)`, etc.

Example: `こんにちは！(excited) 今日はとても良い天気ですね。(happy)`

## API Endpoints

- `GET /` - Web interface
- `POST /generate` - Generate TTS audio
  - `prompt`: Japanese text to synthesize
  - `description`: Voice characteristics description
  - `model`: TTS model to use ("parler", "canary", or "fish")
- `GET /audio/{filename}` - Serve generated audio files

## Configuration

The server runs on `0.0.0.0:8000` by default. Generated audio files are temporarily stored in the system temp directory.

### Model Loading

- Models are automatically downloaded from Hugging Face on first run
- GPU acceleration is used when available (CUDA)
- Graceful fallback to CPU if GPU is not available

## Dependencies

- `torch` - PyTorch for model inference
- `torchaudio` - Audio processing
- `transformers==4.46.1` - Model loading and tokenization
- `parler-tts` - Parler TTS model
- `canary-tts` - Canary TTS model (optional)
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `soundfile` - Audio file handling
- `rubyinserter` - Japanese text processing
- `requests` - HTTP requests for Fish Speech API

## Development

The project uses UV for dependency management. To add new dependencies:

```bash
uv add package-name
```

To run in development mode with auto-reload:

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## License

MIT License - see [LICENSE](LICENSE) file for details

## Credits

This project uses the following models and libraries:

- **Parler TTS** - [2121-8/japanese-parler-tts-mini](https://huggingface.co/2121-8/japanese-parler-tts-mini)
- **Canary TTS** - [2121-8/canary-tts-0.5b](https://huggingface.co/2121-8/canary-tts-0.5b)
- **Fish Speech** - [fishaudio/fish-speech](https://github.com/fishaudio/fish-speech) - OpenAudio S1 model
- **Ruby Inserter** - Japanese text processing for improved pronunciation

Special thanks to the model creators and the open-source community for making these tools available.

## Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues

- Check if the issue already exists in the [Issues](https://github.com/Furious-Green/japanese-tts-webserver/issues) section
- Provide clear description of the problem
- Include steps to reproduce
- Mention your environment (OS, Python version, GPU/CPU)

### Submitting Pull Requests

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes with clear commit messages
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request with a clear description of your changes

### Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise

### Areas for Contribution

- Additional TTS model support
- UI/UX improvements
- Performance optimizations
- Documentation improvements
- Bug fixes and error handling