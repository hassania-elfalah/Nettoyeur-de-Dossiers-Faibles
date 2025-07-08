import os
import time
import shutil
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class FolderCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nettoyeur de Dossiers Faibles")
        self.root.geometry("800x600")
        
        
        self.selected_path = tk.StringVar()
        self.days_threshold = tk.IntVar(value=30)
        self.size_threshold = tk.IntVar(value=100)  
        self.last_access = tk.BooleanVar(value=True)
        self.last_modification = tk.BooleanVar(value=True)
        self.large_folders = tk.BooleanVar(value=True)
        self.empty_folders = tk.BooleanVar(value=True)
        
       
        self.create_widgets()
        
    def create_widgets(self):
       
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
       
        path_frame = ttk.LabelFrame(main_frame, text="Dossier à analyser", padding="10")
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(path_frame, textvariable=self.selected_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(path_frame, text="Parcourir", command=self.browse_folder).pack(side=tk.LEFT, padx=5)
        
       
        options_frame = ttk.LabelFrame(main_frame, text="Critères de recherche", padding="10")
        options_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(options_frame, text="Dossiers non modifiés depuis", variable=self.last_modification).pack(anchor=tk.W)
        ttk.Spinbox(options_frame, from_=1, to=365, textvariable=self.days_threshold, width=5).pack(anchor=tk.W, padx=20)
        ttk.Label(options_frame, text="jours").pack(anchor=tk.W, padx=70)
        
        ttk.Checkbutton(options_frame, text="Dossiers non accédés depuis", variable=self.last_access).pack(anchor=tk.W)
        ttk.Spinbox(options_frame, from_=1, to=365, textvariable=self.days_threshold, width=5).pack(anchor=tk.W, padx=20)
        ttk.Label(options_frame, text="jours").pack(anchor=tk.W, padx=70)
        
        ttk.Checkbutton(options_frame, text="Dossiers volumineux (>", variable=self.large_folders).pack(anchor=tk.W)
        ttk.Spinbox(options_frame, from_=10, to=10000, textvariable=self.size_threshold, width=5).pack(anchor=tk.W, padx=20)
        ttk.Label(options_frame, text="Mo").pack(anchor=tk.W, padx=70)
        
        ttk.Checkbutton(options_frame, text="Dossiers vides", variable=self.empty_folders).pack(anchor=tk.W)
        
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Analyser", command=self.analyze_folders).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Nettoyer", command=self.clean_folders).pack(side=tk.LEFT, padx=5)
        
        
        result_frame = ttk.LabelFrame(main_frame, text="Résultats", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(result_frame, columns=('size', 'last_modified', 'last_accessed'), selectmode='extended')
        self.tree.heading('#0', text='Dossier')
        self.tree.heading('size', text='Taille (Mo)')
        self.tree.heading('last_modified', text='Dernière modification')
        self.tree.heading('last_accessed', text='Dernier accès')
        
        self.tree.column('#0', width=300)
        self.tree.column('size', width=100, anchor=tk.E)
        self.tree.column('last_modified', width=150)
        self.tree.column('last_accessed', width=150)
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        
        self.status = tk.StringVar()
        self.status.set("Prêt")
        ttk.Label(main_frame, textvariable=self.status).pack(fill=tk.X)
        
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.selected_path.set(folder_selected)
    
    def analyze_folders(self):
        if not self.selected_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier à analyser")
            return
            
        self.tree.delete(*self.tree.get_children())
        self.status.set("Analyse en cours...")
        self.root.update()
        
        target_path = self.selected_path.get()
        threshold_date = datetime.now() - timedelta(days=self.days_threshold.get())
        size_limit = self.size_threshold.get() * 1024 * 1024  
        
        for root_dir, dirs, files in os.walk(target_path):
            for dir_name in dirs:
                dir_path = os.path.join(root_dir, dir_name)
                try:
                    dir_info = self.get_folder_info(dir_path)
                    
                   
                    match_criteria = False
                    
                    if self.empty_folders.get() and dir_info['file_count'] == 0:
                        match_criteria = True
                    
                    if self.last_modification.get() and dir_info['last_modified'] < threshold_date:
                        match_criteria = True
                        
                    if self.last_access.get() and dir_info['last_accessed'] < threshold_date:
                        match_criteria = True
                        
                    if self.large_folders.get() and dir_info['size'] > size_limit:
                        match_criteria = True
                    
                    if match_criteria:
                        self.tree.insert('', 'end', text=dir_path, 
                                       values=(f"{dir_info['size']/1024/1024:.2f}",
                                               dir_info['last_modified'].strftime('%Y-%m-%d'),
                                               dir_info['last_accessed'].strftime('%Y-%m-%d')))
                except PermissionError:
                    continue
                except Exception as e:
                    print(f"Erreur avec {dir_path}: {e}")
        
        self.status.set(f"Analyse terminée. {len(self.tree.get_children())} dossiers correspondants trouvés.")
    
    def get_folder_info(self, folder_path):
        total_size = 0
        file_count = 0
        last_modified = datetime.fromtimestamp(0)
        last_accessed = datetime.fromtimestamp(0)
        
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    stat = os.stat(fp)
                    total_size += stat.st_size
                    file_count += 1
                    
                    lm = datetime.fromtimestamp(stat.st_mtime)
                    if lm > last_modified:
                        last_modified = lm
                        
                    la = datetime.fromtimestamp(stat.st_atime)
                    if la > last_accessed:
                        last_accessed = la
                except:
                    continue
        
        return {
            'size': total_size,
            'file_count': file_count,
            'last_modified': last_modified,
            'last_accessed': last_accessed
        }
    
    def clean_folders(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Avertissement", "Aucun dossier sélectionné")
            return
            
        confirm = messagebox.askyesno("Confirmation", 
                                    f"Voulez-vous vraiment supprimer {len(selected_items)} dossiers?",
                                    icon='warning')
        if not confirm:
            return
            
        success = 0
        errors = 0
        
        for item in selected_items:
            folder_path = self.tree.item(item, 'text')
            try:
                shutil.rmtree(folder_path)
                self.tree.delete(item)
                success += 1
            except Exception as e:
                errors += 1
                print(f"Erreur lors de la suppression de {folder_path}: {e}")
        
        self.status.set(f"Opération terminée: {success} dossiers supprimés, {errors} erreurs.")
        messagebox.showinfo("Résultat", f"Suppression terminée: {success} succès, {errors} échecs.")

root = tk.Tk()
app = FolderCleanerApp(root)
root.mainloop()