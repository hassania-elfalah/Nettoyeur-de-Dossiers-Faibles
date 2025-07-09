import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import hashlib
from collections import defaultdict


class CleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nettoyeur de Fichiers et Dossiers")
        self.root.geometry("800x600")
        
        # Variables
        self.min_size = tk.IntVar(value=100)  # Taille minimale en KB
        self.selected_folder = tk.StringVar()
        self.progress = tk.DoubleVar()
        
        # Interface
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sélection de dossier
        folder_frame = ttk.LabelFrame(main_frame, text="Dossier à analyser", padding="10")
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(folder_frame, textvariable=self.selected_folder).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(folder_frame, text="Parcourir", command=self.browse_folder).pack(side=tk.LEFT, padx=5)
        
        # Paramètres
        settings_frame = ttk.LabelFrame(main_frame, text="Paramètres", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="Taille minimale des fichiers (KB):").pack(side=tk.LEFT)
        ttk.Spinbox(settings_frame, from_=1, to=10000, textvariable=self.min_size, width=8).pack(side=tk.LEFT, padx=5)
        
        # Boutons d'action
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Analyser", command=self.analyze).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Nettoyer", command=self.clean).pack(side=tk.LEFT, padx=5)
        
        # Barre de progression
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(progress_frame, text="Progression:").pack(side=tk.LEFT)
        ttk.Progressbar(progress_frame, variable=self.progress, maximum=100).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Résultats
        self.results_text = tk.Text(main_frame, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Barre de défilement
        scrollbar = ttk.Scrollbar(self.results_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
    
    def analyze(self):
        folder = self.selected_folder.get()
        if not folder:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier")
            return
            
        min_size_kb = self.min_size.get()
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Analyse en cours...\n")
        self.root.update()
        
        # Analyse des fichiers trop petits
        small_files = []
        total_files = 0
        small_files_size = 0
        
        for root_dir, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root_dir, file)
                try:
                    file_size_kb = os.path.getsize(file_path) / 1024
                    if file_size_kb < min_size_kb:
                        small_files.append(file_path)
                        small_files_size += file_size_kb
                    total_files += 1
                except:
                    continue
        
        # Analyse des dossiers en double
        duplicate_dirs = self.find_duplicate_dirs(folder)
        
        # Affichage des résultats
        self.results_text.insert(tk.END, f"\n=== Fichiers trop petits (<{min_size_kb} KB) ===\n")
        self.results_text.insert(tk.END, f"{len(small_files)} fichiers trouvés ({small_files_size:.2f} KB au total)\n")
        
        self.results_text.insert(tk.END, "\n=== Dossiers en double ===\n")
        for dirs in duplicate_dirs.values():
            if len(dirs) > 1:
                self.results_text.insert(tk.END, f"\n{len(dirs)} dossiers identiques:\n")
                for d in dirs:
                    self.results_text.insert(tk.END, f"- {d}\n")
        
        self.results_text.insert(tk.END, "\nAnalyse terminée.\n")
    
    def find_duplicate_dirs(self, root_folder):
        dir_hashes = defaultdict(list)
        
        for root_dir, dirs, files in os.walk(root_folder):
            # Ignorer les dossiers vides
            if not dirs and not files:
                continue
                
            dir_hash = self.hash_directory(root_dir)
            dir_hashes[dir_hash].append(root_dir)
        
        return dir_hashes
    
    def hash_directory(self, dir_path):
        hash_obj = hashlib.md5()
        
        for root, _, files in os.walk(dir_path):
            for file in sorted(files):  # Trie les fichiers pour une cohérence
                file_path = os.path.join(root, file)
                try:
                    # Ajouter le nom du fichier et sa taille au hash
                    hash_obj.update(file.encode())
                    hash_obj.update(str(os.path.getsize(file_path)).encode())
                except:
                    continue
        
        return hash_obj.hexdigest()
    
    def clean(self):
        folder = self.selected_folder.get()
        if not folder:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier")
            return
            
        min_size_kb = self.min_size.get()
        
        # Confirmation
        if not messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer les fichiers et dossiers identifiés?"):
            return
            
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Nettoyage en cours...\n")
        self.root.update()
        
        # Suppression des fichiers trop petits
        small_files_count = 0
        small_files_failed = 0
        
        for root_dir, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root_dir, file)
                try:
                    file_size_kb = os.path.getsize(file_path) / 1024
                    if file_size_kb < min_size_kb:
                        try:
                            os.remove(file_path)
                            small_files_count += 1
                        except:
                            small_files_failed += 1
                except:
                    continue
        
        # Suppression des dossiers en double
        duplicate_dirs = self.find_duplicate_dirs(folder)
        duplicate_dirs_count = 0
        duplicate_dirs_failed = 0
        
        for dirs in duplicate_dirs.values():
            if len(dirs) > 1:
                # Garder le premier dossier, supprimer les autres
                for d in dirs[1:]:
                    try:
                        # Suppression récursive du dossier
                        for root, dirs, files in os.walk(d, topdown=False):
                            for file in files:
                                os.remove(os.path.join(root, file))
                            for dir in dirs:
                                os.rmdir(os.path.join(root, dir))
                        os.rmdir(d)
                        duplicate_dirs_count += 1
                    except:
                        duplicate_dirs_failed += 1
        
        # Résultats
        self.results_text.insert(tk.END, "\n=== Résultats du nettoyage ===\n")
        self.results_text.insert(tk.END, f"Fichiers supprimés: {small_files_count} (échecs: {small_files_failed})\n")
        self.results_text.insert(tk.END, f"Dossiers en double supprimés: {duplicate_dirs_count} (échecs: {duplicate_dirs_failed})\n")
        self.results_text.insert(tk.END, "\nNettoyage terminé.\n")


root = tk.Tk()
app = CleanerApp(root)
root.mainloop()
