import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

imports = """from PIL import Image, ImageFilter, ImageTk
import tkinter as tk

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
"""
content = re.sub(r'from PIL import Image, ImageFilter', imports, content)

perspective_class = """

class PerspectiveFixerWindow(ctk.CTkToplevel):
    def __init__(self, master, image_path, callback):
        super().__init__(master)
        self.title(ar("تعديل ميلان الصورة (Perspective Fixer)"))
        self.geometry("900x700")
        self.callback = callback
        self.image_path = image_path
        
        self.points = []
        
        # Load image
        self.original_img_cv = cv2.imread(self.image_path)
        self.original_img_cv = cv2.cvtColor(self.original_img_cv, cv2.COLOR_BGR2RGB)
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

class ModMakerApp"""
content = content.replace("class ModMakerApp", perspective_class)

button_injection = """
        self.img_frame = ctk.CTkFrame(self.tab_add)
        self.img_frame.pack(pady=10)
        
        self.btn_browse_img = ctk.CTkButton(self.img_frame, text=ar("اختر صورة المنتج"), command=self.browse_image)
        self.btn_browse_img.pack(side=tk.LEFT, padx=5)
        
        self.btn_fix_perspective = ctk.CTkButton(self.img_frame, text=ar("تعديل الميلان (اختياري)"), command=self.open_perspective_fixer, fg_color="#F39C12", hover_color="#D68910")
        self.btn_fix_perspective.pack(side=tk.LEFT, padx=5)
"""
# Replace the old browse button logic
old_btn = """        self.btn_browse_img = ctk.CTkButton(self.tab_add, text=ar("اختر صورة المنتج"), command=self.browse_image)
        self.btn_browse_img.pack(pady=10)"""
content = content.replace(old_btn, button_injection)

# Add method to ModMakerApp
fixer_method = """    def open_perspective_fixer(self):
        if not CV2_AVAILABLE:
            messagebox.showerror(ar("خطأ"), ar("يجب تثبيت مكتبة opencv. من فضلك اكتب في موجه الأوامر: pip install opencv-python numpy"))
            return
            
        current_img = self.img_path_var.get()
        if not current_img or not os.path.exists(current_img):
            messagebox.showwarning(ar("تنبيه"), ar("يرجى اختيار صورة أولاً قبل تعديل الميلان!"))
            return
            
        def on_fixed(new_path):
            self.img_path_var.set(new_path)
            self.lbl_img_path.configure(text=ar("تم تعديل الميلان بنجاح!"))
            
        PerspectiveFixerWindow(self.root, current_img, on_fixed)
        
    def add_item(self):"""
content = content.replace("    def add_item(self):", fixer_method)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

