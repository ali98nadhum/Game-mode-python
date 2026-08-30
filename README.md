# Supermarket Simulator Mod Maker 🎮🛒

An ultimate, fully automated GUI tool designed to create custom 3D products (Games, Consoles, Manga, Electronics, and more) for **Supermarket Simulator**. 
With this tool, you can bring any product into the game with zero coding, zero Unity experience, and zero Photoshop skills required!

## ✨ Features

- **🧠 Smart Image Processing (Auto-Crop & Wrap):** 
  Upload any image (whether it's a full wide cover or just a front poster). The built-in AI logic will automatically crop, blur, and wrap your image perfectly around the 3D box edges, completely eliminating the need for Photoshop.
- **📦 Dynamic Box Shapes:** 
  No need to manually edit `products.json` or manipulate 3D models. The UI provides a dropdown to automatically scale your products on the shelf:
  - **Standard** (PS4, PS5, Blu-ray Movies)
  - **Square & Thick** (PS1, CDs, Headsets)
  - **Tall & Thin** (Nintendo Switch Games)
  - **Wide Rectangle** (Keyboards)
  - **Compact Box** (Mobile Phones like iPhone)
- **🎨 Universal Console Wrapping:** 
  For complex console packaging (like PS5 or Xbox Series X), simply provide a front logo or image. The tool will dynamically generate a beautiful, themed "Limited Edition" box wrap covering all sides of the complex 3D model.
- **🌍 Full Arabic UI Support:** 
  Native support for RTL Arabic text rendering on Windows using `arabic_reshaper` and `bidi`.
- **⚡ Fully Automated Configs:** 
  Generates all necessary Unity-compatible `.obj`, `.mtl`, textures, and `products.json` layouts instantly.

## 🛠️ Prerequisites

To run this tool, you need **Python 3** installed on your system.
You also need to install the required Python libraries. Open your terminal (or CMD) and run:

```bash
pip install customtkinter pillow arabic-reshaper python-bidi
```

## 🚀 How to Use

1. **Run the App:**
   Navigate to the `ModMakerCore` directory and run:
   ```bash
   python app.py
   ```

2. **Create a Pack:**
   Go to the "Create Pack" tab. Name your pack, provide an in-game license name, and set a base ID (e.g., `98000`).

3. **Add Products:**
   - Go to the "Add Product" tab.
   - Choose your pack.
   - **For Games & Electronics:** ALWAYS select the `Blu-ray` template! Then, select your desired **Box Shape** from the dropdown (e.g., PS1, Keyboard, Phone).
   - **For Consoles:** Select the specific console template (e.g., `PS5`, `XBoxSeriesX`).
   - Leave the **Smart Processing Checkbox (☑️)** checked.
   - Upload your image (e.g., an iPhone render, a PS4 game cover).
   - Click "Add Product".

4. **Play!**
   Copy the generated folder from `ModMakerCore/packs/` into your Supermarket Simulator mods directory and enjoy your custom items!

## 📂 Project Structure

- `app.py`: The core application and GUI logic.
- `templates/`: Contains the base 3D models (`.obj`, `.mtl`) used for generation. You can drop new `.obj` files here to expand the tool indefinitely.
- `packs/`: The output folder where your generated, ready-to-play mods are saved.
