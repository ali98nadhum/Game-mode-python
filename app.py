import customtkinter as ctk
import os
import json
import shutil
import urllib.request
import random
import re
from PIL import Image, ImageFilter, ImageTk
import tkinter as tk

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from tkinter import filedialog, messagebox

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    messagebox.showerror("Error", "Please install required libraries: pip install arabic-reshaper python-bidi")
    exit()

def ar(text):
    """Helper function to reshape Arabic text and fix RTL direction"""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# --- Config ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKS_DIR = os.path.join(BASE_DIR, "packs")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")



class PerspectiveFixerWindow(ctk.CTkToplevel):
    def __init__(self, master, image_path, callback):
        super().__init__(master)
        self.title(ar("تعديل ميلان الصورة (Perspective Fixer)"))
        self.geometry("900x700")
        self.callback = callback
        self.image_path = image_path
        
        self.points = []
        
        # Load image safely (avoids cv2 Windows Arabic path bug)
        pil_img = Image.open(self.image_path).convert('RGB')
        self.original_img_cv = np.array(pil_img)
        self.h, self.w = self.original_img_cv.shape[:2]
        
        # Calculate scale to fit 800x600 canvas
        self.scale = min(800/self.w, 600/self.h)
        new_w = int(self.w * self.scale)
        new_h = int(self.h * self.scale)
        
        # Resize for display
        img_disp = cv2.resize(self.original_img_cv, (new_w, new_h))
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(img_disp))
        
        # Instructions
        self.lbl_inst = ctk.CTkLabel(self, text=ar("اضغط بالماوس على الزوايا الأربع للكرتون بالترتيب: (أعلى اليسار، أعلى اليمين، أسفل اليمين، أسفل اليسار)"), font=("Arial", 16, "bold"))
        self.lbl_inst.pack(pady=10)
        
        self.canvas = tk.Canvas(self, width=new_w, height=new_h, cursor="crosshair")
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.bind("<Button-1>", self.on_click)
        
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10)
        
        self.btn_reset = ctk.CTkButton(self.btn_frame, text=ar("إعادة التحديد"), command=self.reset_points, fg_color="#E74C3C", hover_color="#C0392B")
        self.btn_reset.pack(side=tk.LEFT, padx=10)
        
        self.btn_apply = ctk.CTkButton(self.btn_frame, text=ar("تأكيد وفرد الصورة"), command=self.apply_fix, state=tk.DISABLED, fg_color="#2ECC71", hover_color="#27AE60")
        self.btn_apply.pack(side=tk.LEFT, padx=10)
        
    def reset_points(self):
        self.points = []
        self.canvas.delete("marker")
        self.canvas.delete("line")
        self.btn_apply.configure(state=tk.DISABLED)
        
    def on_click(self, event):
        if len(self.points) < 4:
            x, y = event.x, event.y
            self.points.append((x, y))
            r = 5
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="red", tags="marker")
            if len(self.points) > 1:
                prev_x, prev_y = self.points[-2]
                self.canvas.create_line(prev_x, prev_y, x, y, fill="red", width=2, tags="line")
            if len(self.points) == 4:
                first_x, first_y = self.points[0]
                self.canvas.create_line(x, y, first_x, first_y, fill="red", width=2, tags="line")
                self.btn_apply.configure(state=tk.NORMAL)
                
    def apply_fix(self):
        pts1 = np.float32([(x / self.scale, y / self.scale) for x, y in self.points])
        
        width_A = np.linalg.norm(pts1[0] - pts1[1])
        width_B = np.linalg.norm(pts1[2] - pts1[3])
        max_width = max(int(width_A), int(width_B))
        
        height_A = np.linalg.norm(pts1[0] - pts1[3])
        height_B = np.linalg.norm(pts1[1] - pts1[2])
        max_height = max(int(height_A), int(height_B))
        
        pts2 = np.float32([[0, 0], [max_width-1, 0], [max_width-1, max_height-1], [0, max_height-1]])
        
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        warped = cv2.warpPerspective(self.original_img_cv, matrix, (max_width, max_height))
        
        import tempfile
        temp_path = os.path.join(tempfile.gettempdir(), "temp_fixed_image.png")
        Image.fromarray(warped).save(temp_path)
        
        self.callback(temp_path)
        self.destroy()

class ModMakerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(ar("صانع مودات سوبر ماركت سيميوليتر"))
        self.geometry("750x750")
        
        os.makedirs(PACKS_DIR, exist_ok=True)
        os.makedirs(TEMPLATES_DIR, exist_ok=True)
        
        if not os.listdir(TEMPLATES_DIR):
            os.makedirs(os.path.join(TEMPLATES_DIR, "Blu-ray"), exist_ok=True)
        
        self.tabview = ctk.CTkTabview(self, width=700, height=700)
        self.tabview.pack(pady=10, padx=10, expand=True, fill="both")
        
        # Tabs
        self.tab_create = self.tabview.add(ar("إنشاء حزمة جديدة"))
        self.tab_add = self.tabview.add(ar("إضافة منتج لحزمة"))
        
        self.setup_create_tab()
        self.setup_add_tab()

    def setup_create_tab(self):
        title_lbl = ctk.CTkLabel(self.tab_create, text=ar("إنشاء حزمة مودات جديدة"), font=("Arial", 22, "bold"))
        title_lbl.pack(pady=20)

        self.pack_name_entry = ctk.CTkEntry(self.tab_create, placeholder_text=ar("اسم مجلد الحزمة (مثلاً: PS5Games)"), width=450, justify="right")
        self.pack_name_entry.pack(pady=15)
        
        self.license_name_entry = ctk.CTkEntry(self.tab_create, placeholder_text=ar("اسم الرخصة داخل اللعبة (مثلاً: ألعاب بلايستيشن 5)"), width=450, justify="right")
        self.license_name_entry.pack(pady=15)
        
        self.base_id_entry = ctk.CTkEntry(self.tab_create, placeholder_text=ar("الرقم التعريفي الأساسي (مثلاً: 98000)"), width=450, justify="right")
        self.base_id_entry.pack(pady=15)
        
        create_btn = ctk.CTkButton(self.tab_create, text=ar("إنشاء الحزمة"), command=self.create_pack, height=45, font=("Arial", 16, "bold"))
        create_btn.pack(pady=30)
        
    def setup_add_tab(self):
        title_lbl = ctk.CTkLabel(self.tab_add, text=ar("إضافة منتج جديد"), font=("Arial", 22, "bold"))
        title_lbl.pack(pady=10)

        # Pack Selection
        self.pack_var = ctk.StringVar(value=ar("اختر الحزمة"))
        self.pack_dropdown = ctk.CTkOptionMenu(self.tab_add, variable=self.pack_var, values=[ar(p) for p in self.get_packs()], width=450)
        self.pack_dropdown.pack(pady=10)
        
        # Template Selection
        self.template_var = ctk.StringVar(value=ar("اختر شكل العلبة (Template)"))
        self.template_dropdown = ctk.CTkOptionMenu(self.tab_add, variable=self.template_var, values=self.get_templates(), width=450)
        self.template_dropdown.pack(pady=10)
        
        self.item_name_entry = ctk.CTkEntry(self.tab_add, placeholder_text=ar("اسم المنتج (مثلاً: قراند 5)"), width=450, justify="right")
        self.item_name_entry.pack(pady=10)
        
        image_frame = ctk.CTkFrame(self.tab_add, fg_color="transparent")
        image_frame.pack(pady=10)
        
        browse_btn = ctk.CTkButton(image_frame, text=ar("استعراض"), width=100, command=self.browse_image, font=("Arial", 14))
        browse_btn.pack(side="left", padx=5)
        
        self.image_entry = ctk.CTkEntry(image_frame, placeholder_text=ar("رابط الصورة أو مسارها من الجهاز"), width=340, justify="right")
        self.image_entry.pack(side="left")
        
        self.btn_fix_perspective = ctk.CTkButton(image_frame, text=ar("تعديل الميلان (اختياري)"), command=self.open_perspective_fixer, fg_color="#F39C12", hover_color="#D68910", width=140)
        self.btn_fix_perspective.pack(side="left", padx=5)        
        self.price_entry = ctk.CTkEntry(self.tab_add, placeholder_text=ar("السعر (اتركه فارغاً لسعر تلقائي مناسب للسوق العراقي)"), width=450, justify="right")
        self.price_entry.pack(pady=10)
        
        # Box Shape Selection
        self.shape_var = ctk.StringVar(value=ar("حجم قياسي (PS4/PS5/Blu-ray)"))
        self.shape_dropdown = ctk.CTkOptionMenu(self.tab_add, variable=self.shape_var, values=[
            ar("حجم قياسي (PS4/PS5/Blu-ray)"),
            ar("مربع وسميك (PS1/CD)"),
            ar("نحيف وطويل (Nintendo Switch)"),
            ar("مستطيل عريض (Keyboard)"),
            ar("علبة هاتف (Mobile Phone)"),
            ar("كرتون كونسول ضخم (PS4/Xbox)")
        ], width=450)
        self.shape_dropdown.pack(pady=10)
        
        self.smart_process_var = ctk.BooleanVar(value=True)
        smart_checkbox = ctk.CTkCheckBox(self.tab_add, text=ar("المعالجة الذكية وقص الصور الآلي (اتركه مفعلاً دائماً ✅)"), variable=self.smart_process_var, font=("Arial", 14, "bold"))
        smart_checkbox.pack(pady=15)
        
        add_btn = ctk.CTkButton(self.tab_add, text=ar("إضافة المنتج"), command=self.add_item, height=45, font=("Arial", 16, "bold"))
        add_btn.pack(pady=20)
        
        self.tabview.configure(command=self.refresh_ui)
        
    def refresh_ui(self):
        packs = self.get_packs()
        if not packs:
            display_packs = [ar("لا توجد حزم")]
            self.pack_var.set(ar("لا توجد حزم"))
        else:
            display_packs = [ar(p) for p in packs]
            if self.pack_var.get() not in display_packs:
                self.pack_var.set(display_packs[0])
        self.pack_dropdown.configure(values=display_packs)
            
        templates = self.get_templates()
        if not templates:
            display_templates = [ar("لا توجد قوالب")]
            self.template_var.set(ar("لا توجد قوالب"))
        else:
            display_templates = templates
            if self.template_var.get() not in display_templates:
                self.template_var.set(display_templates[0])
        self.template_dropdown.configure(values=display_templates)
        
    def get_packs(self):
        if not os.path.exists(PACKS_DIR): return []
        packs = [d for d in os.listdir(PACKS_DIR) if os.path.isdir(os.path.join(PACKS_DIR, d))]
        return packs

    def get_templates(self):
        if not os.path.exists(TEMPLATES_DIR): return []
        templates = [d for d in os.listdir(TEMPLATES_DIR) if os.path.isdir(os.path.join(TEMPLATES_DIR, d))]
        templates = [t for t in templates if not t.endswith("_Dummy")]
        return templates

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp")])
        if file_path:
            self.image_entry.delete(0, 'end')
            self.image_entry.insert(0, file_path)

    def create_pack(self):
        pack_name = self.pack_name_entry.get().strip()
        license_name = self.license_name_entry.get().strip()
        base_id = self.base_id_entry.get().strip()
        
        if not pack_name or not license_name or not base_id:
            messagebox.showerror(ar("خطأ"), ar("جميع الحقول مطلوبة!"))
            return
            
        try:
            base_id = int(base_id)
        except ValueError:
            messagebox.showerror(ar("خطأ"), ar("يجب أن يكون الرقم التعريفي الأساسي رقماً!"))
            return
            
        pack_path = os.path.join(PACKS_DIR, pack_name)
        if os.path.exists(pack_path):
            messagebox.showerror(ar("خطأ"), ar("مجلد الحزمة موجود مسبقاً! يرجى اختيار اسم مختلف."))
            return
            
        os.makedirs(os.path.join(pack_path, "objects_meshes"))
        os.makedirs(os.path.join(pack_path, "objects_textures"))
        os.makedirs(os.path.join(pack_path, "products_icons"))
        
        products_json = {
            "$schema": "../schemas/product_config.json",
            "ProductLicenses": [
                {
                    "ID": base_id,
                    "LicenseName": license_name,
                    "RequiredPlayerLevel": 1,
                    "PurchasingCost": 0,
                    "Products": []
                }
            ]
        }
        
        with open(os.path.join(pack_path, "products.json"), "w", encoding="utf-8") as f:
            json.dump(products_json, f, indent=4, ensure_ascii=False)
            
        messagebox.showinfo(ar("نجاح"), ar("تم إنشاء الحزمة بنجاح! يمكنك الآن إضافة المنتجات."))
        self.pack_name_entry.delete(0, 'end')
        self.license_name_entry.delete(0, 'end')
        self.base_id_entry.delete(0, 'end')
        self.refresh_ui()
        self.pack_var.set(ar(pack_name))

    def open_perspective_fixer(self):
        if not CV2_AVAILABLE:
            messagebox.showerror(ar("خطأ"), ar("يجب تثبيت مكتبة opencv. من فضلك اكتب في موجه الأوامر: pip install opencv-python numpy"))
            return
            
        current_img = self.image_entry.get().strip()
        if not current_img or not os.path.exists(current_img):
            messagebox.showwarning(ar("تنبيه"), ar("يرجى استعراض واختيار صورة صحيحة أولاً قبل تعديل الميلان!"))
            return
            
        def on_fixed(new_path):
            self.image_entry.delete(0, 'end')
            self.image_entry.insert(0, new_path)
            messagebox.showinfo(ar("نجاح"), ar("تم تعديل الميلان بنجاح! يمكنك الآن الإضافة."))
            
        PerspectiveFixerWindow(self, current_img, on_fixed)
        
    def add_item(self):
        pack_name_display = self.pack_var.get()
        if pack_name_display in [ar("اختر الحزمة"), ar("لا توجد حزم"), ""]:
            messagebox.showerror(ar("خطأ"), ar("يرجى إنشاء واختيار حزمة أولاً!"))
            return
            
        pack_name = self.pack_var.get() 
        for p in self.get_packs():
            if ar(p) == pack_name_display:
                pack_name = p
                break
            
        template_name = self.template_var.get()
        if template_name in [ar("اختر شكل العلبة (Template)"), ar("لا توجد قوالب"), ""]:
            messagebox.showerror(ar("خطأ"), ar("يرجى اختيار شكل العلبة (القالب) أولاً!"))
            return
            
        item_name = self.item_name_entry.get().strip()
        img_source = self.image_entry.get().strip()
        price_str = self.price_entry.get().strip()
        shape_choice = self.shape_var.get()
        
        if not item_name or not img_source:
            messagebox.showerror(ar("خطأ"), ar("اسم المنتج والصورة مطلوبان!"))
            return
            
        try:
            price = float(price_str) if price_str else round(random.uniform(1.00, 2.50), 2)
        except ValueError:
            messagebox.showerror(ar("خطأ"), ar("صيغة السعر غير صحيحة!"))
            return
            
        pack_path = os.path.join(PACKS_DIR, pack_name)
        self.process_item_addition(pack_path, item_name, img_source, price, template_name, self.smart_process_var.get(), shape_choice)
        
    def process_item_addition(self, pack_path, title, image_source, price, template_name, use_smart_process, shape_choice):
        json_path = os.path.join(pack_path, "products.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror(ar("خطأ"), ar("تعذرت قراءة ملف products.json!"))
            return
            
        license_data = data["ProductLicenses"][0]
        products = license_data["Products"]
        
        item_index = len(products) + 1
        base_id = license_data["ID"]
        next_id = products[-1]["ID"] + 1 if products else base_id + 1
        
        temp_img = os.path.join(pack_path, "temp_img.jpg")
        
        try:
            # 1. Fetch Template info
            template_dir = os.path.join(TEMPLATES_DIR, template_name)
            template_obj = os.path.join(template_dir, "template.obj")
            template_mtl = os.path.join(template_dir, "template.mtl")
            
            template_img_path = None
            for ext in ["jpg", "jpeg", "png", "webp"]:
                p = os.path.join(template_dir, f"template.{ext}")
                if os.path.exists(p):
                    template_img_path = p
                    break
                    
            if not os.path.exists(template_obj) or not os.path.exists(template_mtl):
                messagebox.showerror(ar("خطأ"), ar("قوالب الـ 3D مفقودة من هذا المجلد! يرجى إضافة المجسمات أولاً."))
                return
                
            tex_w, tex_h = 3173, 1962 # default fallback
            if template_img_path:
                with Image.open(template_img_path) as t_img:
                    tex_w, tex_h = t_img.size

            # 2. Fetch User Image
            if image_source.startswith("http://") or image_source.startswith("https://"):
                req = urllib.request.Request(image_source, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(temp_img, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            else:
                shutil.copy(image_source, temp_img)
                
            img = Image.open(temp_img).convert("RGB")
            
            icon_path = os.path.join(pack_path, "products_icons", f"item{item_index}.jpg")
            tex_path = os.path.join(pack_path, "objects_textures", f"item{item_index}.jpg")
            
            icon = img.resize((1519, 1750), Image.Resampling.LANCZOS)
            icon.save(icon_path)
            
            # 3. Image Processing Logic
            if use_smart_process:
                is_game = any(word in template_name.lower() for word in ["game", "blu-ray", "manga"])
                is_custom_box = shape_choice != ar("حجم قياسي (PS4/PS5/Blu-ray)")
                
                if is_game or is_custom_box:
                    composite = Image.new('RGB', (3173, 1962), color=(15, 20, 35))
                    front_w, spine_w, back_w = 1450, 273, 1450
                    
                    aspect_ratio = img.width / img.height
                    
                    if aspect_ratio > 1.2 and not is_custom_box:
                        # FULL COVER PROVIDED (Auto-Crop)
                        if shape_choice == ar("مربع وسميك (PS1/CD)"):
                            expected_front_ratio = 1.0
                        elif shape_choice == ar("نحيف وطويل (Nintendo Switch)"):
                            expected_front_ratio = 0.6
                        else:
                            expected_front_ratio = 0.739 # Standard
                            
                        actual_front_w = int(img.height * expected_front_ratio)
                        
                        if actual_front_w * 2 >= img.width:
                            actual_front_w = int(img.width * 0.45)
                            
                        back_part = img.crop((0, 0, actual_front_w, img.height))
                        front_part = img.crop((img.width - actual_front_w, 0, img.width, img.height))
                        spine_part = img.crop((actual_front_w, 0, img.width - actual_front_w, img.height))
                        
                        composite.paste(back_part.resize((back_w, 1962), Image.Resampling.LANCZOS), (0, 0))
                        composite.paste(spine_part.resize((spine_w, 1962), Image.Resampling.LANCZOS), (back_w, 0))
                        composite.paste(front_part.resize((front_w, 1962), Image.Resampling.LANCZOS), (back_w + spine_w, 0))
                    else:
                        # FRONT COVER ONLY (Generate spine and blurred back)
                        front_cover = img.resize((front_w, 1962), Image.Resampling.LANCZOS)
                        composite.paste(front_cover, (back_w + spine_w, 0))
                        
                        back_cover = img.resize((back_w, 1962), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(30))
                        darkener = Image.new('RGB', (back_w, 1962), color=(0, 0, 0))
                        back_cover = Image.blend(back_cover, darkener, alpha=0.5)
                        composite.paste(back_cover, (0, 0))
                        
                        spine_cover = img.resize((spine_w, 1962), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(15))
                        spine_cover = Image.blend(spine_cover, Image.new('RGB', (spine_w, 1962), color=(0, 0, 0)), alpha=0.2)
                        composite.paste(spine_cover, (back_w, 0))
                    
                    final_texture = composite.resize((tex_w, tex_h), Image.Resampling.LANCZOS)
                    final_texture.save(tex_path)
                else:
                    bg = img.resize((tex_w, tex_h), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(50))
                    darkener = Image.new('RGB', (tex_w, tex_h), color=(0, 0, 0))
                    bg = Image.blend(bg, darkener, alpha=0.4)
                    
                    fg_h = int(tex_h * 0.45)
                    fg_w = int(img.width * (fg_h / img.height))
                    fg = img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
                    
                    bg.paste(fg, ((tex_w - fg_w) // 2, (tex_h - fg_h) // 2))
                    
                    logo_h = int(tex_h * 0.2)
                    logo_w = int(img.width * (logo_h / img.height))
                    logo = img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                    
                    margin_x = int(tex_w * 0.05)
                    margin_y = int(tex_h * 0.05)
                    
                    bg.paste(logo, (margin_x, margin_y))
                    bg.paste(logo, (tex_w - logo_w - margin_x, margin_y))
                    bg.paste(logo, (margin_x, tex_h - logo_h - margin_y))
                    bg.paste(logo, (tex_w - logo_w - margin_x, tex_h - logo_h - margin_y))
                    
                    final_texture = bg
                    final_texture.save(tex_path)
            else:
                final_texture = img.resize((tex_w, tex_h), Image.Resampling.LANCZOS)
                final_texture.save(tex_path)
                
            # 4. Copy 3D Models
            new_obj = os.path.join(pack_path, "objects_meshes", f"item{item_index}.obj")
            new_mtl = os.path.join(pack_path, "objects_meshes", f"item{item_index}.mtl")
            
            is_custom_shape = shape_choice != ar("حجم قياسي (PS4/PS5/Blu-ray)")
            
            if is_custom_shape:
                # Generate a unit cube with pivot at bottom center (Y: 0 to 1)
                box_obj = f"mtllib item{item_index}.mtl\n"
                # Vertices: 1-4 Front, 5-8 Back (Y changed from -0.5,0.5 to 0.0,1.0)
                box_obj += "v -0.5 0.0 0.5\nv 0.5 0.0 0.5\nv 0.5 1.0 0.5\nv -0.5 1.0 0.5\n"
                box_obj += "v -0.5 0.0 -0.5\nv 0.5 0.0 -0.5\nv 0.5 1.0 -0.5\nv -0.5 1.0 -0.5\n"
                # Normals
                box_obj += "vn 0 0 1\nvn 0 0 -1\nvn -1 0 0\nvn 1 0 0\nvn 0 1 0\nvn 0 -1 0\n"
                
                # If image is upside down in Unity, we might need to invert V (1.0 - V). 
                # Let's invert V because Unity reads textures from bottom-up, but PIL saves top-down.
                # Actually, standard is V=0 is bottom. Let's swap 0 and 1 for V.
                # Front (1-4) BL, BR, TR, TL -> mapped to TopLeft to BottomRight if V is inverted?
                # Let's map it normally but flipped vertically: V=1.0 is bottom, V=0.0 is top.
                box_obj += "vt 0.543 1.0\nvt 1.0 1.0\nvt 1.0 0.0\nvt 0.543 0.0\n" # Front 
                box_obj += "vt 0.457 1.0\nvt 0.0 1.0\nvt 0.0 0.0\nvt 0.457 0.0\n" # Back
                box_obj += "vt 0.457 1.0\nvt 0.543 1.0\nvt 0.543 0.0\nvt 0.457 0.0\n" # Spine/Sides
                
                box_obj += "usemtl Material\n"
                # Front face (+Z)
                box_obj += "f 1/1/1 4/4/1 3/3/1 2/2/1\n"
                # Back face (-Z)
                box_obj += "f 6/5/2 7/8/2 8/7/2 5/6/2\n"
                # Left face (-X)
                box_obj += "f 5/9/3 8/12/3 4/11/3 1/10/3\n"
                # Right face (+X)
                box_obj += "f 2/9/4 3/12/4 7/11/4 6/10/4\n"
                # Top face (+Y)
                box_obj += "f 4/9/5 8/12/5 7/11/5 3/10/5\n"
                # Bottom face (-Y)
                box_obj += "f 5/9/6 1/12/6 2/11/6 6/10/6\n" 
                
                with open(new_obj, "w") as f:
                    f.write(box_obj)
                    
                box_mtl = "newmtl Material\n"
                box_mtl += "Ka 1.000 1.000 1.000\nKd 1.000 1.000 1.000\nKs 0.000 0.000 0.000\n"
                box_mtl += f"map_Kd ../objects_textures/item{item_index}.jpg\n"
                with open(new_mtl, "w") as f:
                    f.write(box_mtl)
            else:
                with open(template_obj, "r") as f:
                    obj_content = f.read()
                obj_content = re.sub(r'mtllib\s+.*\.mtl', f'mtllib item{item_index}.mtl', obj_content)
                with open(new_obj, "w") as f:
                    f.write(obj_content)
                    
                with open(template_mtl, "r") as f:
                    mtl_content = f.read()
                mtl_content = re.sub(r'map_Kd\s+.*', f'map_Kd ../objects_textures/item{item_index}.jpg', mtl_content)
                with open(new_mtl, "w") as f:
                    f.write(mtl_content)
                
            # Determine Box Shape Scale (meters)
            if shape_choice == ar("مربع وسميك (PS1/CD)"):
                local_scale = [0.15, 0.15, 0.02]
            elif shape_choice == ar("نحيف وطويل (Nintendo Switch)"):
                local_scale = [0.10, 0.17, 0.015]
            elif shape_choice == ar("مستطيل عريض (Keyboard)"):
                local_scale = [0.45, 0.15, 0.05]
            elif shape_choice == ar("علبة هاتف (Mobile Phone)"):
                local_scale = [0.08, 0.16, 0.04]
            elif shape_choice == ar("كرتون كونسول ضخم (PS4/Xbox)"):
                local_scale = [0.40, 0.30, 0.15]
            else:
                local_scale = [1.2, 1.2, 1.2]
                
            is_console = (shape_choice == ar("كرتون كونسول ضخم (PS4/Xbox)")) or ("ps" in template_name.lower()) or ("xbox" in template_name.lower()) or ("console" in template_name.lower())
            
            if is_console:
                grid_in_box = {
                  "boxSize": "_20x20x20",
                  "productCount": 6,
                  "firstObjectPosition": [0.05, 0.32, -0.25],
                  "productAngles": [0.0, 0.0, 0.0],
                  "spacing": [0.17, 0.04, 0.10],
                  "productPlacement": [1,6],
                  "scaleMultiplier": 0.65
                }
                grid_in_storage = {
                  "boxSize": "_20x20x10",
                  "productCount": 3,
                  "firstObjectPosition": [0.0, 0.08, -0.18],
                  "productAngles": [0.0, 180.0, 0.0],
                  "spacing": [0.9, 0.9, 0.145],
                  "productPlacement": [1,3],
                  "scaleMultiplier": 1.0
                }
                item_grid_size = [2, 1]
                product_amount_on_purchase = 6
            else:
                grid_in_box = {
                    "boxSize": "_20x10x7",
                    "productCount": 20,
                    "firstObjectPosition": [0.27, -0.01, 0.0],
                    "productAngles": [0.0, 90.0, 0.0],
                    "spacing": [0.028, 0.0, 0.0],
                    "productPlacement": [20,1],
                    "scaleMultiplier": 1.0
                }
                grid_in_storage = {
                    "boxSize": "_20x10x7",
                    "productCount": 60,
                    "firstObjectPosition": [0.31, 0.01, -0.21],
                    "productAngles": [0.0, 0.0, 0.0],
                    "spacing": [0.21, 0.0, 0.027],
                    "productPlacement": [4,15],
                    "scaleMultiplier": 1.1
                }
                item_grid_size = [2, 1]
                product_amount_on_purchase = 20
                
            # 5. Update JSON
            new_product = {
                "ID": next_id,
                "ProductName": title,
                "ProductBrand": "ModMaker",
                "ProductIcon": f"products_icons/item{item_index}.jpg",
                "BoxIcon": f"products_icons/item{item_index}.jpg",
                "ProductDisplayType": "SHELF",
                "Category": "EDIBLE",
                "ProductPrefab": {
                    "objPath": f"objects_meshes/item{item_index}.obj",
                    "mtlPath": f"objects_meshes/item{item_index}.mtl",
                    "localScale": local_scale
                },
                "ProductAmountOnPurchase": product_amount_on_purchase,
                "BasePrice": price,
                "MinDynamicPrice": round(price * 1.5, 2),
                "MaxDynamicPrice": round(price * 2.5, 2),
                "OptimumProfitRate": 100.0,
                "MaxProfitRate": 120.0,
                "GridLayoutInBox": grid_in_box,
                "GridLayoutInStorage": grid_in_storage,
                "ItemGridSize": item_grid_size
            }
            
            products.append(new_product)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            if os.path.exists(temp_img):
                os.remove(temp_img)
                
            messagebox.showinfo(ar("نجاح"), ar(f"تمت إضافة المنتج بنجاح باستخدام قالب {template_name}!"))
            self.item_name_entry.delete(0, 'end')
            self.image_entry.delete(0, 'end')
            self.price_entry.delete(0, 'end')
            
        except Exception as e:
            messagebox.showerror(ar("خطأ"), ar(f"فشلت عملية الإضافة: {e}"))

if __name__ == "__main__":
    app = ModMakerApp()
    app.mainloop()
