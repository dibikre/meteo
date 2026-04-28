#import sys
#sys.path.append(r"c:\\users\\dibi\\appdata\\local\\packages\\pythonsoftwarefoundation.python.3.13_qbz5n2kfra8p0\\localcache\\local-packages\\python313\\site-packages")
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from outils import connect_db, DIRECTION_PROJET

def afficher_Profil(grande_bordure, id_user):
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    copie_recuper_chemin_image = None
    
    # Sélectionner une image sur le disque
    def select_image():
        nonlocal copie_recuper_chemin_image
        chemin_img = [("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        recuperer_chemin_image = filedialog.askopenfilename(title="Sélectionner une Image", filetypes=chemin_img)
        if recuperer_chemin_image:
            copie_recuper_chemin_image = recuperer_chemin_image
            update_image_preview()
    
    # Remplacer l'image actuelle par l'image sélectionnée
    def update_image_preview():
        if copie_recuper_chemin_image:
            try:
                img = Image.open(copie_recuper_chemin_image)
                affiche_img = ctk.CTkImage(light_image=img, size=(150, 150))
                label_img.configure(image=affiche_img, text="")
                label_img.image = affiche_img
            except Exception as e:
                print(f"Erreur lors du chargement de l'image: {e}")
                label_img.configure(text="Erreur de chargement")

    # Fonction qui change la photo
    def change_photo():
        if copie_recuper_chemin_image:
            try:
                # Obtenir le slogan de l'utilisateur pour créer le chemin relatif
                conn = connect_db()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT slogan FROM utilisateurs WHERE id_user = ?", (id_user,))
                    slogan = cursor.fetchone()[0]

                    # Définir le chemin relatif pour stocker l'image
                    dir_relatif = DIRECTION_PROJET / f"accessoires/indentification/utilisateurs/{slogan}"
                    dir_relatif.mkdir(parents=True, exist_ok=True)

                    # Copier l'image sélectionnée à l'emplacement relatif
                    chem_rel_image = dir_relatif / f"{slogan}.jpg"
                    img = Image.open(copie_recuper_chemin_image)
                    img.save(chem_rel_image)

                    # Enregistrer le chemin souhaité dans la base de données
                    relative_image_db_path = f"{slogan}/{slogan}.jpg"
                    cursor.execute("UPDATE utilisateurs SET photo = ? WHERE id_user = ?", (relative_image_db_path, id_user))
                    conn.commit()

                    messagebox.showinfo("Succès", "Photo de profil mise à jour.")
                else:
                    raise Exception("Connexion à la base de données échouée.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de la mise à jour de la photo : {e}")
        else:
            messagebox.showwarning("Avertissement", "Aucune image sélectionnée")

    # Changer les données de l'utilisateur
    def update_profile():
        username = username_entry.get()
        password = password_entry.get()
        slogan = slogan_entry.get()

        try:
            conn = connect_db()
            if conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE utilisateurs
                        SET username = ?, password = ?, slogan = ?
                        WHERE id_user = ?
                    """, (username, password, slogan, id_user))
                messagebox.showinfo("Succès", "Informations du profil mises à jour.")
            else:
                raise Exception("Connexion à la base de données échouée.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la mise à jour du profil : {e}")

    # Étiquette pour l'image
    label_img = ctk.CTkLabel(grande_bordure, text="Aucune image sélectionnée", font=("Arial", 16), width=150, height=150)
    label_img.pack(pady=20)

    # Bouton pour sélectionner une image
    select_button = ctk.CTkButton(grande_bordure, text="Sélectionner une Image", command=select_image)
    select_button.pack(pady=10)

    # Bouton pour changer la photo de profil
    change_button = ctk.CTkButton(grande_bordure, text="Remplacer votre Photo", fg_color="#EEEEEE", corner_radius=15, hover_color="#483f3e", font=("Arial Bold", 11), text_color="#000000", border_width=1, command=change_photo)
    change_button.pack(pady=10)

    # Cadre pour les informations du profil
    info_frame = ctk.CTkFrame(grande_bordure)
    info_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(info_frame, text="Mettre à jour les informations du profil", font=("Arial", 16)).pack(pady=5)

    # Entrées pour le nom d'utilisateur, le mot de passe et le slogan
    username_entry = ctk.CTkEntry(info_frame, placeholder_text="Nom d'utilisateur")
    username_entry.pack(pady=5)

    password_entry = ctk.CTkEntry(info_frame, placeholder_text="Mot de passe", show="*")
    password_entry.pack(pady=5)

    slogan_entry = ctk.CTkEntry(info_frame, placeholder_text="Slogan")
    slogan_entry.pack(pady=5)

    # Bouton pour mettre à jour le profil
    update_button = ctk.CTkButton(info_frame, text="Mettre à jour le profil", corner_radius=15, fg_color="#EEEEEE", hover_color="#483f3e", font=("Arial Bold", 11), text_color="#000000", border_width=1, command=update_profile)
    update_button.pack(pady=10)