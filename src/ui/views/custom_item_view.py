import os
import random
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
from src.utils.helpers import ar, PACKS_DIR
from src.core.pack_manager import PackManager
from src.core.item_processor import ItemProcessor
from src.ui.components.perspective_fixer import PerspectiveFixerWindow, CV2_AVAILABLE

class CustomItemView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # UI state variables
        self.pack_var = ctk.StringVar(value=ar("اختر الحزمة"))
        self.template_var = ctk.StringVar(value=ar("اختر شكل العلبة (Template)"))
        self.shape_var = ctk.StringVar(value=ar("حجم قياسي (PS4/PS5/Blu-ray)"))
        self.smart_process_var = ctk.BooleanVar(value=True)
        self.img_path_var = ctk.StringVar(value="")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create a scrollable frame since this view has many controls
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_lbl = ctk.CTkLabel(self.scroll_frame, text=ar("إضافة منتج مخصص"), font=("Arial", 28, "bold"))
        title_lbl.pack(pady=20)

        # Dropdowns
        dropdown_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        dropdown_frame.pack(pady=10, fill="x")
        
        self.pack_dropdown = ctk.CTkOptionMenu(dropdown_frame, variable=self.pack_var, values=[], width=350, height=40, font=("Arial", 14))
        self.pack_dropdown.pack(side="left", padx=10, expand=True)
        
        self.template_dropdown = ctk.CTkOptionMenu(dropdown_frame, variable=self.template_var, values=[], width=350, height=40, font=("Arial", 14))
        self.template_dropdown.pack(side="right", padx=10, expand=True)
        
        # Product Name
        self.item_name_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text=ar("اسم المنتج (مثلاً: قراند 5)"), width=500, height=45, justify="right", font=("Arial", 14))
        self.item_name_entry.pack(pady=15)
        
        # Image Selection Frame
        img_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#2b2b2b", corner_radius=10)
        img_frame.pack(pady=15, fill="x", padx=40)
        
        lbl_img_title = ctk.CTkLabel(img_frame, text=ar("صورة المنتج"), font=("Arial", 16, "bold"))
        lbl_img_title.pack(pady=(10, 0))
        
        img_controls = ctk.CTkFrame(img_frame, fg_color="transparent")
        img_controls.pack(pady=10)
        
        self.btn_browse = ctk.CTkButton(img_controls, text=ar("استعراض صورة..."), command=self.browse_image, width=150, height=35)
        self.btn_browse.pack(side="left", padx=10)
        
        self.btn_fix = ctk.CTkButton(img_controls, text=ar("تعديل الميلان"), command=self.open_perspective_fixer, width=150, height=35, fg_color="#F39C12", hover_color="#D68910")
        self.btn_fix.pack(side="left", padx=10)
        
        self.lbl_img_path = ctk.CTkLabel(img_frame, text=ar("لم يتم اختيار صورة"), text_color="gray", font=("Arial", 12))
        self.lbl_img_path.pack(pady=(0, 10))
        
        # Price
        self.price_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text=ar("السعر (اتركه فارغاً لسعر تلقائي مناسب)"), width=500, height=45, justify="right", font=("Arial", 14))
        self.price_entry.pack(pady=15)
        
        # Shape Options
        lbl_shape = ctk.CTkLabel(self.scroll_frame, text=ar("شكل وحجم الكرتون (في الرف)"), font=("Arial", 16, "bold"))
        lbl_shape.pack(pady=(15, 5))
        
        self.shape_dropdown = ctk.CTkOptionMenu(self.scroll_frame, variable=self.shape_var, values=[
            ar("حجم قياسي (PS4/PS5/Blu-ray)"),
            ar("مربع وسميك (PS1/CD)"),
            ar("نحيف وطويل (Nintendo Switch)"),
            ar("مستطيل عريض (Keyboard)"),
            ar("علبة هاتف (Mobile Phone)"),
            ar("كرتون كونسول ضخم (PS4/Xbox)")
        ], width=500, height=40, font=("Arial", 14))
        self.shape_dropdown.pack(pady=5)
        
        # Smart Checkbox
        smart_checkbox = ctk.CTkCheckBox(self.scroll_frame, text=ar("المعالجة الذكية وقص الصور الآلي (اتركه مفعلاً دائماً ✅)"), variable=self.smart_process_var, font=("Arial", 14, "bold"))
        smart_checkbox.pack(pady=20)
        
        # Submit Button
        add_btn = ctk.CTkButton(self.scroll_frame, text=ar("إضافة المنتج"), command=self.add_item, height=50, width=300, font=("Arial", 18, "bold"), fg_color="#27AE60", hover_color="#2ECC71")
        add_btn.pack(pady=30)
        
        self.refresh_data()
        
    def refresh_data(self):
        packs = PackManager.get_packs()
        if not packs:
            display_packs = [ar("لا توجد حزم")]
            self.pack_var.set(ar("لا توجد حزم"))
        else:
            display_packs = [ar(p) for p in packs]
            if self.pack_var.get() not in display_packs:
                self.pack_var.set(display_packs[0])
        self.pack_dropdown.configure(values=display_packs)
            
        templates = PackManager.get_templates()
        if not templates:
            display_templates = [ar("لا توجد قوالب")]
            self.template_var.set(ar("لا توجد قوالب"))
        else:
            display_templates = templates
            if self.template_var.get() not in display_templates:
                self.template_var.set(display_templates[0])
        self.template_dropdown.configure(values=display_templates)

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp")])
        if file_path:
            self.img_path_var.set(file_path)
            self.lbl_img_path.configure(text=file_path, text_color="white")

    def open_perspective_fixer(self):
        if not CV2_AVAILABLE:
            messagebox.showerror(ar("خطأ"), ar("يجب تثبيت مكتبة opencv. من فضلك اكتب في موجه الأوامر: pip install opencv-python numpy"))
            return
            
        current_img = self.img_path_var.get().strip()
        if not current_img or not os.path.exists(current_img):
            messagebox.showwarning(ar("تنبيه"), ar("يرجى استعراض واختيار صورة صحيحة أولاً قبل تعديل الميلان!"))
            return
            
        def on_fixed(new_path):
            self.img_path_var.set(new_path)
            self.lbl_img_path.configure(text=ar("تم تعديل الميلان بنجاح!"), text_color="#2ECC71")
            
        PerspectiveFixerWindow(self.master, current_img, on_fixed)

    def add_item(self):
        pack_name_display = self.pack_var.get()
        if pack_name_display in [ar("اختر الحزمة"), ar("لا توجد حزم"), ""]:
            messagebox.showerror(ar("خطأ"), ar("يرجى إنشاء واختيار حزمة أولاً!"))
            return
            
        # Reverse map to get raw pack name
        pack_name = next((p for p in PackManager.get_packs() if ar(p) == pack_name_display), pack_name_display)
            
        template_name = self.template_var.get()
        if template_name in [ar("اختر شكل العلبة (Template)"), ar("لا توجد قوالب"), ""]:
            messagebox.showerror(ar("خطأ"), ar("يرجى اختيار شكل العلبة (القالب) أولاً!"))
            return
            
        item_name = self.item_name_entry.get().strip()
        img_source = self.img_path_var.get().strip()
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
        
        try:
            ItemProcessor.process_item_addition(
                pack_path=pack_path,
                title=item_name,
                image_source=img_source,
                price=price,
                template_name=template_name,
                use_smart_process=self.smart_process_var.get(),
                shape_choice=shape_choice
            )
            messagebox.showinfo(ar("نجاح"), ar(f"تمت إضافة المنتج بنجاح باستخدام قالب {template_name}!"))
            self.item_name_entry.delete(0, 'end')
            self.img_path_var.set("")
            self.lbl_img_path.configure(text=ar("لم يتم اختيار صورة"), text_color="gray")
            self.price_entry.delete(0, 'end')
        except Exception as e:
            messagebox.showerror(ar("خطأ"), ar(str(e)))
