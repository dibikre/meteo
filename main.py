#import sys
#sys.path.append(r"c:\\users\\dibi\\appdata\\local\\packages\\pythonsoftwarefoundation.python.3.13_qbz5n2kfra8p0\\localcache\\local-packages\\python313\\site-packages")
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from pathlib import Path
import connections
import accueil
import historiques
import profil
from outils import connect_db, DIRECTION_PROJET

def charger_donnee_user(id_user):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT photo, slogan FROM utilisateurs WHERE id_user = ?", (id_user,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result
    return None, None

def main_app(id_user):
    # Initialiser l'application
    ecran = ctk.CTk()
    ecran.title("APPLICATION METEO PRECISE")

    l_ecran, h_ecran = ecran.winfo_screenwidth(), ecran.winfo_screenheight()
    largeur_fenetre, hauteur_fenetre = int(l_ecran * 0.99), int(h_ecran * 1)
    positionX, positionY = int((l_ecran - largeur_fenetre) / 2), int((h_ecran - hauteur_fenetre) / 2)
    ecran.geometry(f"{largeur_fenetre}x{hauteur_fenetre}+{positionX}+{positionY}")

    logo = DIRECTION_PROJET / "accessoires/logo/logo.ico"
    ecran.iconbitmap(logo)

    # Créer un cadre pour le menu
    menu_frame = ctk.CTkFrame(ecran)
    menu_frame.pack(side="top", fill="x")

    # Créer un frame principal pour le contenu
    grande_bordure = ctk.CTkFrame(ecran, corner_radius=15)
    grande_bordure.pack(expand=True, fill="both", padx=6, pady=(5, 20))

    # Charger les informations de l'utilisateur
    photo, slogan = charger_donnee_user(id_user)

    # Construire le chemin complet de la photo
    dossier_utilisateurs = DIRECTION_PROJET / "accessoires/indentification/utilisateurs"
    photo_path = dossier_utilisateurs / photo if photo else None

    # Créer un cadre pour afficher la photo et le slogan
    user_info_frame = ctk.CTkFrame(menu_frame)
    user_info_frame.pack(side="right", padx=20, pady=10)

    if photo_path and photo_path.exists():
        try:
            image = Image.open(photo_path)
            photo_img = ctk.CTkImage(light_image=image, size=(50, 50))
            photo_label = ctk.CTkLabel(user_info_frame, image=photo_img, text="")
            photo_label.pack(side="left", padx=10)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image: {e}")
    else:
        print("Chemin de la photo invalide ou photo manquante")

    slogan_label = ctk.CTkLabel(user_info_frame, text=slogan if slogan else "Slogan non défini")
    slogan_label.pack(side="left", padx=10)

    # Fonction pour quitter l'application avec confirmation
    def quitter_app():
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment quitter l'application ?"):
            ecran.destroy()

    # Ajouter le bouton "Quitter"
    quit_button = ctk.CTkButton(user_info_frame, text="Quitter", command=quitter_app, fg_color="white", hover_color="gray")
    quit_button.pack(side="right", padx=10)

    # Fonction pour mettre à jour la couleur des boutons du menu
    def update_button_colors(selected_button):
        buttons = [accueil_button, historiques_button, profil_button]
        for button in buttons:
            button.configure(fg_color="white", text_color="black")
        selected_button.configure(fg_color="black", text_color="white")

    # Fonctions pour les boutons
    def on_accueil_click():
        update_button_colors(accueil_button)
        for widget in grande_bordure.winfo_children():
            widget.destroy()
        accueil.afficher_Accueil(grande_bordure, id_user)

    def on_historiques_click():
        update_button_colors(historiques_button)
        for widget in grande_bordure.winfo_children():
            widget.destroy()
        historiques.afficher_Historiques(grande_bordure, id_user)

    def on_profil_click():
        update_button_colors(profil_button)
        for widget in grande_bordure.winfo_children():
            widget.destroy()
        profil.afficher_Profil(grande_bordure, id_user)

    # Créer les boutons du menu
    accueil_button = ctk.CTkButton(menu_frame, text="Accueil", command=on_accueil_click, fg_color="white", text_color="black", hover_color="lightgray")
    accueil_button.pack(side="left", padx=(500, 0), pady=10)

    historiques_button = ctk.CTkButton(menu_frame, text="Historiques", command=on_historiques_click, fg_color="white", text_color="black", hover_color="lightgray")
    historiques_button.pack(side="left", padx=0, pady=10)

    profil_button = ctk.CTkButton(menu_frame, text="Profil", command=on_profil_click, fg_color="white", text_color="black", hover_color="lightgray")
    profil_button.pack(side="left", padx=0, pady=10)

    # Afficher la vue par défaut
    on_accueil_click()

    # Lancer la boucle principale
    ecran.mainloop()

# Démarrer par la fenêtre de connexion
connections.start_login(main_app)