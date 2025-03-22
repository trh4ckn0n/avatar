import bpy
import openai
import requests
import os
from flask import Flask, render_template, request, jsonify
import threading

# --- CONFIGURATION ---
api_key = "VOTRE_CLE_OPENAI"

# --- 1️⃣ CRÉATION DU MODÈLE 3D AVEC BLENDER ---
def create_hacker_avatar():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Création de la tête
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1.5))
    head = bpy.context.object
    head.name = "Head"

    # Ajout du masque Guy Fawkes
    bpy.ops.import_scene.obj(filepath="guy_fawkes_mask.obj")

    # Ajout du hoodie
    bpy.ops.import_scene.obj(filepath="hacker_hoodie.obj")

    # Exportation au format GLB
    bpy.ops.export_scene.gltf(filepath="static/hacker_avatar.glb", export_format='GLB')

    print("✅ Avatar 3D généré avec succès !")

# --- 2️⃣ GÉNÉRATION D'UNE TEXTURE AVEC DALL·E ---
def generate_texture():
    response = openai.Image.create(
        model="dall-e-3",
        prompt="Cyberpunk hacker hoodie texture with neon green lines and futuristic symbols",
        n=1,
        size="1024x1024",
        api_key=api_key
    )
    texture_url = response['data'][0]['url']
    img_data = requests.get(texture_url).content
    with open("static/hacker_texture.png", "wb") as f:
        f.write(img_data)
    print("✅ Texture IA téléchargée :", texture_url)

# --- 3️⃣ CRÉATION DU SERVEUR WEB FLASK ---
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get("message")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_message}],
        api_key=api_key
    )
    return jsonify({"response": response["choices"][0]["message"]["content"]})

# --- LANCEMENT DU SERVEUR ---
def start_server():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    threading.Thread(target=create_hacker_avatar).start()
    threading.Thread(target=generate_texture).start()
    threading.Thread(target=start_server).start()
