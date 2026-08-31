import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from src.utils.helpers import ar

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

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
