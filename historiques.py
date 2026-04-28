#import sys
#sys.path.append(r"c:\\users\\dibi\\appdata\\local\\packages\\pythonsoftwarefoundation.python.3.13_qbz5n2kfra8p0\\localcache\\local-packages\\python313\\site-packages")
import customtkinter as ctk
import sqlite3
from PIL import Image, ImageTk
from outils import connect_db, DIRECTION_PROJET

ELEMENTS_PAR_PAGE = 6

def afficher_Historiques(grande_bordure, id_user):
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    dossier_utilisateurs = DIRECTION_PROJET / "accessoires/indentification/utilisateurs"

    zone_recherche = ctk.CTkFrame(grande_bordure, fg_color="transparent")
    zone_recherche.pack(side="top", anchor="center", padx=20, pady=(15, 20))

    titre_h = ctk.CTkLabel(zone_recherche, text="HISTORIQUES", font=("Arial", 40, "bold"))
    titre_h.pack(side="left", padx=(5, 5))

    cadre_tableau = ctk.CTkFrame(grande_bordure, fg_color="#a6a1a1")
    cadre_tableau.pack(expand=True, side="top", anchor="n", pady=(10, 5))

    entete_tab = ["ID", "Photo", "Consulté par", "Ville", "Pays", "Température", "Vitesse Vent", "Date", "Description", "Taux Humidité", "Levé Soleil", "Couché Soleil", "Niveau Mer"]

    for col, indice_entete in enumerate(entete_tab):
        label_entete = ctk.CTkLabel(cadre_tableau, text=indice_entete, font=("Arial", 15, "bold"), fg_color="#540a87", text_color="#ffffff")
        label_entete.grid(row=0, column=col, padx=8, pady=10)

    conn = connect_db()
    data = []
    if conn:
        try:
            cursor = conn.cursor()
            query = '''
            SELECT i.id, u.photo, u.slogan, i.ville, p.nom_pays, i.temp, i.vitesse_vent, i.date, i.desc, i.taux_hmdt, i.leve_sol, i.couche_sol, i.niv_mer
            FROM info_meteo i
            JOIN utilisateurs u ON i.id_user = u.id_user
            JOIN tab_pays p ON i.id_pays = p.id_pays
            WHERE u.id_user = ?
            ORDER BY i.date DESC
            '''
            cursor.execute(query, (id_user,))
            data = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des historiques: {e}")
        finally:
            conn.close()
    
    if not data:
        print("Aucune donnée à afficher.")
        return

    # Fonction de filtrage
    def filtrer_donnees():
        utilisateur_selectionne = dropdown_user.get()
        ville_saisie = champ_ville.get().strip().lower()

        utilisateur_filtre = [d for d in data if d[2].lower() == utilisateur_selectionne.lower()]
        ville_filtre = [d for d in utilisateur_filtre if not ville_saisie or d[3].lower() == ville_saisie]

        return ville_filtre

    # Pagination
    nombre_page = 0

    def afficher_page(page):
        # Vider le tableau actuel
        for widget in cadre_tableau.winfo_children():
            widget.grid_forget()

        # Afficher les en-têtes à nouveau
        for col, indice_entete in enumerate(entete_tab):
            label_entete = ctk.CTkLabel(cadre_tableau, text=indice_entete, font=("Arial", 15, "bold"), fg_color="#540a87", text_color="#ffffff")
            label_entete.grid(row=0, column=col, padx=5, pady=2)

        # Filtrer les données
        donnee_filtrees = filtrer_donnees()

        # Calculer les indices de début et de fin pour les éléments de la page actuelle
        debut_index = page * ELEMENTS_PAR_PAGE
        fin_index = debut_index + ELEMENTS_PAR_PAGE
        donnee_page = donnee_filtrees[debut_index:fin_index]

        # Ajouter les données de la page au tableau
        for index_colonne, donnees_colonne in enumerate(donnee_page, start=1):
            for col_index, item in enumerate(donnees_colonne):
                if col_index == 1:  # Photo
                    photo_path = dossier_utilisateurs / item
                    try:
                        image = Image.open(photo_path).resize((50, 50))
                        photo = ImageTk.PhotoImage(image)
                        label_ligne = ctk.CTkLabel(cadre_tableau, image=photo, text="", width=50, height=50)
                        label_ligne.image = photo  # Conserver une référence à l'image
                    except Exception as e:
                        print(f"Erreur lors du chargement de l'image {photo_path}: {e}")
                        label_ligne = ctk.CTkLabel(cadre_tableau, text="N/A", font=("Arial", 10))
                else:
                    if isinstance(item, float):
                        item = f"{item:.2f}"
                    label_ligne = ctk.CTkLabel(cadre_tableau, text=item, font=("Arial", 10))
                label_ligne.grid(row=index_colonne, column=col_index, padx=5, pady=5)

    def suivant():
        nonlocal nombre_page
        if (nombre_page + 1) * ELEMENTS_PAR_PAGE < len(filtrer_donnees()):
            nombre_page += 1
            afficher_page(nombre_page)

    def precedent():
        nonlocal nombre_page
        if nombre_page > 0:
            nombre_page -= 1
            afficher_page(nombre_page)

    # Ajouter les boutons de pagination et les filtres
    btn_precedent = ctk.CTkButton(grande_bordure, text="<   Précédent", corner_radius=15, hover_color="#ffffff", command=precedent)
    btn_precedent.pack(side="left", padx=(10, 0), pady=10)

    # Dropdown pour sélectionner l'utilisateur
    utilisateurs = list(set(d[2] for d in data))  # Supprimez "Tous" ici
    dropdown_user = ctk.StringVar()
    dropdown_menu = ctk.CTkOptionMenu(grande_bordure, variable=dropdown_user, values=utilisateurs)
    dropdown_menu.pack(side="left", padx=(10, 10), pady=10)
    if utilisateurs:  # Vérifie qu'il y a au moins un utilisateur
        dropdown_user.set(utilisateurs[0])  # Définit le premier utilisateur comme sélection par défaut

    # Champ de saisie pour filtrer par ville
    champ_ville = ctk.CTkEntry(grande_bordure, placeholder_text="Rechercher par ville")
    champ_ville.pack(side="left", padx=(10, 10), pady=10)

    btn_suivant = ctk.CTkButton(grande_bordure, text="Suivant   >", corner_radius=15, hover_color="#ffffff", command=suivant)
    btn_suivant.pack(side="right", padx=(0, 10), pady=10)

    # Afficher la première page
    afficher_page(nombre_page)

    # Rafraîchir l'affichage chaque fois qu'un filtre est modifié
    dropdown_menu.configure(command=lambda _: afficher_page(0))
    champ_ville.bind("<Return>", lambda _: afficher_page(0))