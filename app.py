import bpy
import openai
import requests
import os
from flask import Flask, render_template, request, jsonify, send_file
import threading

# --- CONFIGURATION ---
api_key = "VOTRE_CLE_OPENAI"
app = Flask(__name__)

# --- 1️⃣ AVATAR 3D (Génération avec Blender) ---
def create_hacker_avatar():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1.5))
    head = bpy.context.object
    head.name = "Head"

    bpy.ops.import_scene.obj(filepath="guy_fawkes_mask.obj")
    bpy.ops.import_scene.obj(filepath="hacker_hoodie.obj")

    bpy.ops.export_scene.gltf(filepath="static/hacker_avatar.glb", export_format='GLB')
    print("✅ Avatar 3D généré avec succès !")

# --- 2️⃣ TEXTURE IA (DALL·E) ---
def generate_texture():
    response = openai.Image.create(
        model="dall-e-3",
        prompt="Cyberpunk hacker hoodie texture with neon green symbols",
        n=1,
        size="1024x1024",
        api_key=api_key
    )
    texture_url = response['data'][0]['url']
    img_data = requests.get(texture_url).content
    with open("static/hacker_texture.png", "wb") as f:
        f.write(img_data)
    print("✅ Texture IA téléchargée :", texture_url)

# --- 3️⃣ GPT-4 + SYNTHÈSE VOCALE ---
@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get("message")
    
    # 🔹 Génération de la réponse IA
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_message}],
        api_key=api_key
    )
    bot_reply = response["choices"][0]["message"]["content"]

    # 🔹 Synthèse Vocale (TTS OpenAI)
    speech_response = openai.Audio.create(
        model="tts-1",
        voice="alloy",  # Voix réaliste : "alloy", "echo", "fable", "onyx", "nova", "shimmer"
        input=bot_reply,
        api_key=api_key
    )
    
    speech_file = "static/hacker_voice.mp3"
    with open(speech_file, "wb") as f:
        f.write(speech_response['data'])

    return jsonify({"response": bot_reply, "audio": "/static/hacker_voice.mp3"})

# --- LANCEMENT DU SERVEUR ---
def start_server():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    threading.Thread(target=create_hacker_avatar).start()
    threading.Thread(target=generate_texture).start()
    threading.Thread(target=start_server).start()
