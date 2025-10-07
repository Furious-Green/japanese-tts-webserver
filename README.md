# Japanese TTS Web Server

A FastAPI-based web server for Japanese Text-to-Speech synthesis supporting multiple TTS models.

### About Furious Green

[Furious Green](https://furiousgreen.co) is a Japan-based technology training company focused on AI, machine learning, and generative models. We build open tools and demos like this one to help engineers and researchers experiment with the latest AI technologies — in this case, Japanese Text-to-Speech models.

## Features

- **Multi-Model Support**: Choose between Parler TTS, Canary TTS, and Fish Speech models
- **Web Interface**: Clean, user-friendly web interface for text input and audio playback
- **Japanese Text Processing**: Automatic ruby insertion for better pronunciation
- **Real-time Generation**: Generate and play audio directly in the browser
- **Model Comparison**: Easy switching between different TTS models

## Supported Models

### Parler TTS (Required)
- **Model**: [2121-8/japanese-parler-tts-mini](https://huggingface.co/2121-8/japanese-parler-tts-mini)
- **Description**: Uses separate voice description for fine-grained control over voice characteristics
- **VRAM**: ~2-4 GB
- **Disk Space**: ~1-2 GB

### Canary TTS (Optional)
- **Model**: [2121-8/canary-tts-0.5b](https://huggingface.co/2121-8/canary-tts-0.5b)
- **Description**: Uses chat template format with system/user messages for advanced conversational AI-based approach
- **VRAM**: ~4-6 GB
- **Disk Space**: ~2-3 GB

### Fish Speech (Optional)
- **Model**: [OpenAudio S1](https://github.com/fishaudio/fish-speech) (via API server)
- **Description**: Zero-shot voice cloning with reference audio support
- **VRAM**: ~4 GB minimum, 12 GB recommended
- **Disk Space**: ~1 GB (S1-mini) or ~8 GB (S1 full)
- **Special Features**:
  - Emotion markers: `(angry)`, `(sad)`, `(excited)`, `(surprised)`, etc.
  - Special effects: `(laughing)`, `(whispering)`, `(sighing)`, etc.
  - Example: `こんにちは！(excited) 今日はとても良い天気ですね。(happy)`

## Requirements

- Python 3.10+
- CUDA-compatible GPU (recommended, or CPU with reduced performance)
- UV package manager
- **Total VRAM**: 12-16 GB recommended if loading multiple models
- **Total Disk Space**: ~5-10 GB for model downloads and cache

**Note**: First run will download models from Hugging Face, which may take 10-30 minutes depending on your internet connection.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Furious-Green/japanese-tts-webserver.git
cd japanese-tts-webserver
```

### 2. Install base dependencies
```bash
uv sync
```

### 3. Install model dependencies

#### For Parler TTS (Required)
```bash
uv pip install git+https://github.com/getuka/RubyInserter.git
uv pip install git+https://github.com/huggingface/parler-tts.git
```

#### For Canary TTS (Optional)
```bash
# RubyInserter is already installed from Parler TTS setup above
uv pip install git+https://github.com/getuka/canary-tts.git
```

#### For Fish Speech (Optional)
Fish Speech requires a separate API server. Follow these steps:

1. Clone and set up the Fish Speech repository:
```bash
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech
# Follow the installation instructions in their README
```

2. Install system dependencies (Linux):
```bash
sudo apt install portaudio19-dev libsox-dev ffmpeg
```

3. Download the model weights:
```bash
# First install huggingface_hub CLI
uv tool install huggingface_hub[cli]

# Download the OpenAudio S1-mini model weights
uvx --from huggingface_hub[cli] hf download fishaudio/openaudio-s1-mini --local-dir checkpoints/openaudio-s1-mini
```

4. Start the Fish Speech API server:
```bash
uv run --python 3.12 python -m tools.api_server \
  --listen 0.0.0.0:8080 \
  --llama-checkpoint-path "checkpoints/openaudio-s1-mini" \
  --decoder-checkpoint-path "checkpoints/openaudio-s1-mini/codec.pth" \
  --decoder-config-name modded_dac_vq
```

The web interface will automatically detect the running Fish Speech API server.

## Usage

### Starting the Server

```bash
# Option 1: Using the main script
uv run python main.py

# Option 2: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Using the Web Interface

1. Open your browser and navigate to `http://localhost:8000`
2. Select your preferred TTS model from the dropdown menu
3. Enter Japanese text in the text area
4. Customize the voice description based on the selected model
5. Click "Generate Speech" to create and play the audio

## API Endpoints

- `GET /` - Web interface
- `POST /generate` - Generate TTS audio
  - `prompt`: Japanese text to synthesize
  - `description`: Voice characteristics description
  - `model`: TTS model to use ("parler", "canary", or "fish")
- `GET /audio/{filename}` - Serve generated audio files

## Configuration

- **Server Host/Port**: Default is `0.0.0.0:8000` (can be changed in `main.py`)
- **Generated Audio Files**: Temporarily stored in system temp directory
- **Model Loading**: Models are automatically downloaded from Hugging Face on first run
- **GPU Acceleration**: Automatically used when CUDA is available, with graceful fallback to CPU

## Development

### Adding Dependencies
```bash
uv add package-name
```

### Running in Development Mode
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
- **Ruby Inserter** - [getuka/RubyInserter](https://github.com/getuka/RubyInserter) - Japanese text processing

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
