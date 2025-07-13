# AI-Assets
AI research assets
Ideas , links , area of exploration

## LLM Chat Application

This repository includes a small NiceGUI application for chatting with a local LLM served via Ollama.

### Usage
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Install [Ollama](https://ollama.com) and download a model, e.g.:
   ```bash
   ollama pull gemma3:1b
   ```
3. Run the application:
   ```bash
   python app.py
   ```

The interface allows sending messages, viewing streaming answers in Markdown and stopping generation with the `Stop` button or `Ctrl+C`.
