from __future__ import annotations
import asyncio
import json
from typing import AsyncGenerator, List, Dict

import httpx
from nicegui import ui

MODEL_NAME = 'gemma3:1b'
OLLAMA_URL = 'http://localhost:11434/api/chat'

chat_history: List[Dict[str, str]] = []
stop_signal = False

async def stream_ollama(prompt: str) -> AsyncGenerator[str, None]:
    """Stream tokens from Ollama chat endpoint."""
    global stop_signal
    payload = {
        'model': MODEL_NAME,
        'messages': chat_history + [{'role': 'user', 'content': prompt}],
        'stream': True,
    }
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream('POST', OLLAMA_URL, json=payload) as response:
            async for line in response.aiter_lines():
                if stop_signal:
                    break
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                token = data.get('message', {}).get('content')
                if token:
                    yield token
                if data.get('done'):
                    break

async def on_send_click() -> None:
    """Handle sending of the user's prompt."""
    prompt = prompt_area.value.strip()
    if not prompt:
        return
    prompt_area.value = ''
    send_button.disable()
    stop_button.enable()
    chat_history.append({'role': 'user', 'content': prompt})
    chat_history.append({'role': 'assistant', 'content': ''})
    render_history()
    async for token in stream_ollama(prompt):
        chat_history[-1]['content'] += token
        render_history()
        await asyncio.sleep(0)  # allow UI to update
    send_button.enable()
    stop_button.disable()
    render_history()

def on_stop_click() -> None:
    global stop_signal
    stop_signal = True

def render_history() -> None:
    content = ''
    for entry in chat_history:
        role = 'User' if entry['role'] == 'user' else 'Assistant'
        content += f'**{role}:** {entry["content"]}\n\n'
    history_markdown.content = content
    ui.run_javascript(
        f'document.getElementById("{history_markdown.id}").scrollTop = '
        f'document.getElementById("{history_markdown.id}").scrollHeight'
    )

prompt_area = ui.textarea(label='Message', placeholder='Type your question here...', auto_resize=True).style('width: 100%')

with ui.row():
    send_button = ui.button('Wyślij', on_click=on_send_click).classes('send-button')
    stop_button = ui.button('Stop', on_click=on_stop_click, disabled=True).classes('stop-button')

history_markdown = ui.markdown('').style('height: 400px; overflow-y: auto;')

ui.add_head_html(
    """
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const btn = document.querySelector('.send-button');
            if (btn && !btn.disabled) { btn.click(); }
        }
        if (e.key === 'c' && e.ctrlKey) {
            e.preventDefault();
            const btn = document.querySelector('.stop-button');
            if (btn && !btn.disabled) { btn.click(); }
        }
    });
    </script>
    """
)

ui.run()
