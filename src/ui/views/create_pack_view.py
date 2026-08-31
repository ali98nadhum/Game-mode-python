import customtkinter as ctk
from tkinter import messagebox
from src.utils.helpers import ar
from src.core.pack_manager import PackManager

class CreatePackView(ctk.CTkFrame):
    def __init__(self, master, refresh_callback):
        super().__init__(master, fg_color="transparent")
        self.refresh_callback = refresh_callback
        
        self.setup_ui()
        
    def setup_ui(self):
        title_lbl = ctk.CTkLabel(self, text=ar("إنشاء حزمة مودات جديدة"), font=("Arial", 28, "bold"))
        title_lbl.pack(pady=40)

        self.pack_name_entry = ctk.CTkEntry(self, placeholder_text=ar("اسم مجلد الحزمة (مثلاً: PS5Games)"), width=500, height=45, justify="right", font=("Arial", 16))
        self.pack_name_entry.pack(pady=15)
        
        self.license_name_entry = ctk.CTkEntry(self, placeholder_text=ar("اسم الرخصة داخل اللعبة (مثلاً: ألعاب بلايستيشن 5)"), width=500, height=45, justify="right", font=("Arial", 16))
        self.license_name_entry.pack(pady=15)
        
        self.base_id_entry = ctk.CTkEntry(self, placeholder_text=ar("الرقم التعريفي الأساسي (مثلاً: 98000)"), width=500, height=45, justify="right", font=("Arial", 16))
        self.base_id_entry.pack(pady=15)
        
        create_btn = ctk.CTkButton(self, text=ar("إنشاء الحزمة"), command=self.create_pack, height=50, width=300, font=("Arial", 18, "bold"), fg_color="#3498DB", hover_color="#2980B9")
        create_btn.pack(pady=40)
        
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
            
        try:
            PackManager.create_pack(pack_name, license_name, base_id)
            messagebox.showinfo(ar("نجاح"), ar("تم إنشاء الحزمة بنجاح! يمكنك الآن إضافة المنتجات."))
            self.pack_name_entry.delete(0, 'end')
            self.license_name_entry.delete(0, 'end')
            self.base_id_entry.delete(0, 'end')
            
            # Refresh other views (e.g. dropdowns in the Add Item view)
            if self.refresh_callback:
                self.refresh_callback()
                
        except Exception as e:
            messagebox.showerror(ar("خطأ"), ar(str(e)))
