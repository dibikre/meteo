#import sys
#sys.path.append(r"c:\\users\\dibi\\appdata\\local\\packages\\pythonsoftwarefoundation.python.3.13_qbz5n2kfra8p0\\localcache\\local-packages\\python313\\site-packages")
from tkinter import messagebox, filedialog
import customtkinter as ctk
from PIL import Image
from datetime import datetime
from outils import connect_db, DIRECTION_PROJET

# Configuration des chemins
auth_dir_ico = DIRECTION_PROJET / "accessoires/indentification/icones"
dossier_user = DIRECTION_PROJET / "accessoires/indentification/utilisateurs"
logo = DIRECTION_PROJET / "accessoires/logo/logo.ico"

def verif_user(username, password):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM utilisateurs WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            return user is not None
        finally:
            conn.close()
    return False

def obtenir_id_user(username):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_user FROM utilisateurs WHERE username=?", (username,))
            user_id = cursor.fetchone()
            return user_id[0] if user_id else None
        finally:
            conn.close()

def login(main_app):
    username = username_saisie.get()
    password = password_saisie.get()
    if verif_user(username, password):
        messagebox.showinfo("Succès", "Connexion réussie!")
        ecran.destroy()  # Fermer l'écran de connexion
        id_user = obtenir_id_user(username)
        main_app(id_user)  # Lancer l'application principale avec l'id_user
    else:
        messagebox.showwarning("Échec", "Nom d'utilisateur ou mot de passe incorrect.")

def switch_frame(hide_frame, show_frame):
    hide_frame.pack_forget()
    show_frame.pack(expand=True, fill='both')

def charger_image():
    global chemin_img
    chemin_img = filedialog.askopenfilename(filetypes=[("type d'image", "*.png;*.jpg;*.jpeg;*.gif")])
    if chemin_img:
        img = Image.open(chemin_img).convert("RGB")
        img_tk = ctk.CTkImage(dark_image=img, light_image=img, size=(100, 100))
        icon_label.configure(image=img_tk)
        icon_label.image = img_tk

def ajouter_utilisateur(username, password, slogan, chemin_photo):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO utilisateurs (slogan, username, password, photo, date_creation)
            VALUES (?, ?, ?, ?, ?)
        ''', (slogan, username, password, chemin_photo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

def creer_compte():
    nom_utilisateur, mot_de_passe, user_slogan = i_user.get(), i_mot_pass.get(), slogan.get()
    if nom_utilisateur and mot_de_passe and user_slogan and chemin_img:
        utilisateur_dir = dossier_user / user_slogan  # Chemin pour stocker l'image
        utilisateur_dir.mkdir(parents=True, exist_ok=True)

        chemin_photo = f"{user_slogan}/{user_slogan}.jpg"  # Chemin relatif pour la base de données
        full_path = utilisateur_dir / f"{user_slogan}.jpg"  # Chemin complet pour enregistrer l'image

        Image.open(chemin_img).convert("RGB").save(full_path, "JPEG")  # Enregistrez l'image

        ajouter_utilisateur(nom_utilisateur, mot_de_passe, user_slogan, chemin_photo)
        switch_frame(register_frame, login_frame)
    else:
        messagebox.showwarning("Veuillez remplir tous les champs et charger une image.")

def start_login(main_app):
    global ecran, username_saisie, password_saisie, login_frame, register_frame, chemin_img, icon_label, i_user, i_mot_pass, slogan

    # Initialisation de la fenêtre principale
    ecran = ctk.CTk()
    ecran.title("APPLICATION METEO PRECISE")
    ecran.geometry("600x480")
    ecran.resizable(0, 0)
    ecran.iconbitmap(logo)

    def create_ctk_image(file_path, size):
        img_data = Image.open(auth_dir_ico / file_path)
        return ctk.CTkImage(dark_image=img_data, light_image=img_data, size=size)

    side_img = create_ctk_image("slide_login.jpg", (300, 480))
    icon_user = create_ctk_image("user.png", (20, 20))
    password_icon = create_ctk_image("cle.png", (17, 17))
    icone_portail = create_ctk_image("ins_icone.png", (17, 17))
    logo_estem = create_ctk_image("estem.png", (100, 100))

    login_frame = ctk.CTkFrame(ecran)
    ctk.CTkLabel(login_frame, text="", image=side_img).pack(expand=True, side="right")
    cadre_gauche = ctk.CTkFrame(login_frame, width=300, height=480, fg_color="#ffffff")
    cadre_gauche.pack_propagate(0)
    cadre_gauche.pack(expand=True, side="left")

    def create_label(frame, text, image, font_size, pady=(0, 0)):
        return ctk.CTkLabel(frame, text=text, image=image, text_color="#601E88", justify="left", font=("Arial Bold", font_size), compound="left").pack(anchor="w", pady=pady, padx=(25, 0))

    create_label(cadre_gauche, "", logo_estem, 24)
    create_label(cadre_gauche, "BIENVENU", None, 24, pady=(0, 5))
    create_label(cadre_gauche, "Se connecter a votre compte", None, 12)

    create_label(cadre_gauche, "  nom d'utilisateur:", icon_user, 14, pady=(38, 0))
    username_saisie = ctk.CTkEntry(cadre_gauche, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000")
    username_saisie.pack(anchor="w", padx=(25, 0))

    create_label(cadre_gauche, "  mot de passe:", password_icon, 14, pady=(21, 0))
    password_saisie = ctk.CTkEntry(cadre_gauche, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000", show="*")
    password_saisie.pack(anchor="w", padx=(25, 0))

    ctk.CTkButton(cadre_gauche, text="se connecter", fg_color="#601E88", hover_color="#E44982", font=("Arial Bold", 12), text_color="#ffffff", width=225, command=lambda: login(main_app)).pack(anchor="w", pady=(40, 0), padx=(25, 0))
    ctk.CTkButton(cadre_gauche, text="S'inscrire ?", fg_color="#EEEEEE", hover_color="#483f3e", font=("Arial Bold", 9), text_color="#000000", width=225, image=icone_portail, command=lambda: switch_frame(login_frame, register_frame)).pack(anchor="w", pady=(20, 0), padx=(25, 0))

    register_frame = ctk.CTkFrame(ecran)
    i_zone = ctk.CTkFrame(register_frame, corner_radius=18, fg_color="#ffffff")
    i_zone.pack(pady=10, padx=10, fill="both", expand=True)

    icon_label = ctk.CTkLabel(i_zone, text="", image=create_ctk_image("ins_icone.png", (100, 100)), corner_radius=18, fg_color="transparent")
    icon_label.pack(pady=10)

    def inscription_entry(frame, placeholder):
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, fg_color="#bfb3b3", border_color="#bfb3b3")
        entry.pack(pady=5, padx=60, fill="x")
        return entry

    i_user = inscription_entry(i_zone, "Nom d'utilisateur")
    i_mot_pass = ctk.CTkEntry(i_zone, placeholder_text="Mot de passe", show="*", fg_color="#bfb3b3", border_color="#601E88")
    i_mot_pass.pack(pady=5, padx=60, fill="x")
    slogan = inscription_entry(i_zone, "Votre slogan")

    ctk.CTkButton(i_zone, text="Charger une image", command=charger_image).pack(pady=5, padx=10)
    ctk.CTkButton(i_zone, text="Créer le compte", command=creer_compte).pack(pady=20)
    ctk.CTkButton(i_zone, text="  Se connecter ?  ", corner_radius=18, fg_color="#EEEEEE", hover_color="#483f3e", font=("Arial Bold", 9), text_color="#000000", command=lambda: switch_frame(register_frame, login_frame)).pack(pady=10, padx=10)

    ctk.CTkLabel(i_zone, text="", image=logo_estem).pack(side="bottom", anchor="s", pady=(0, 0), padx=10)

    login_frame.pack(expand=True, fill='both')

    ecran.mainloop()