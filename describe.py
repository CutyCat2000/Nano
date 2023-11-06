import asyncio
import websockets
import random
import string
import json
import re


def generate_random_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def replace_image_links(text):
    # Regular expression pattern to match URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    # Find all URLs in the text
    urls = re.findall(url_pattern, text)

    # Replace URLs with the specified format
    for url in urls:
        replacement = f"<fake_token_around_image><image:{url}><fake_token_around_image>"
        text = text.replace(url, replacement)

    return text

async def describe(image_link):
    prompt = replace_image_links(image_link) + "\ngive me 3 bullet points with what can be seen in the picture. (SHORT SENTENCES)"
    uri = "wss://HuggingFaceM4-idefics-playground.hf.space/queue/join"
    async with websockets.connect(uri) as websocket:
        session_hash = generate_random_string(100)
        n = await websocket.recv()
        await websocket.send(json.dumps({"fn_index":4,"session_hash":session_hash}))
        n = json.loads(n)
        while not n["msg"] == "send_data":
            n = await websocket.recv()
            n = json.loads(n)
        data = { "data": [ "HuggingFaceM4/idefics-80b-instruct", prompt, [], None, "Top P Sampling", 0.4, 512, 1, 0.8 ], "event_data": None, "fn_index": 3, "session_hash": session_hash }
        await websocket.send(json.dumps(data))
        n = await websocket.recv()
        n = json.loads(n)
        while not n["msg"] == "process_completed":
            n = await websocket.recv()
            n = json.loads(n)
        return n["output"]["data"][2][len(n["output"]["data"][2])-1][1].replace("<img src='https://huggingface.co/spaces/HuggingFaceM4/idefics_playground/resolve/main/IDEFICS_logo.png' width='45'>","")