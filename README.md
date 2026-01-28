# ViGen

ViGen is a desktop application powered by AI that enables users to generate videos from simple ideas or detailed scripts. It leverages Google's Gemini models for story and script generation, and Veo for video synthesis, wrapped in a modern PyQt6 interface.

## Features

- **Idea to Video**: Generate a full story, character portraits, script, and final video from a single idea.
- **Script to Video**: Input a script and character details to produce a video directly.
- **Multimodal AI**: Uses Google Gemini for text/image logical processing and Veo for video generation.
- **Character Consistency**: Maintains character appearance across scenes using reference images.
- **Cross-Platform**: Available for Windows and macOS (Intel & Apple Silicon).

## Installation

### Download Release

Go to the Releases page and download the executable for your operating system:

- Windows: ViGen_Windows.exe
- macOS: ViGen_macOS_Silicon.zip (or Intel)

### Run from Source

1. Clone the repository.
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    (Or use `uv` / `poetry` as configured in the project)
3. Run the application:
    ```bash
    python -m gui.main
    ```

## Configuration

Upon first launch, ViGen will create a `configs` folder with template files. You must provide your own API keys for the application to function.

1. Open `configs/idea2video.yaml` and `configs/script2video.yaml`.
2. Enter your keys:
    - `chat_model`: OpenRouter API Key (or other supported provider).
    - `image_generator`: Google Cloud/Gemini API Key.
    - `video_generator`: Google Cloud/Gemini API Key.

## Technology Stack

- **GUI**: PyQt6, Qt-Material
- **AI Orchestration**: LangChain
- **Models**: Google Gemini 2.0 Flash, Imagen 3, Veo 2
- **Video Processing**: MoviePy

## License

This project is licensed under the MIT License.
