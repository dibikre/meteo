#import sys
#sys.path.append(r"c:\users\dibi\appdata\local\packages\pythonsoftwarefoundation.python.3.13_qbz5n2kfra8p0\localcache\local-packages\python313\site-packages")
from datetime import datetime
from PIL import Image
import customtkinter as ctk
import tkintermapview
import requests
from outils import connect_db, horloge, id_pays_par_code, nom_pays_par_code, DIRECTION_PROJET

# Configuration initiale
horloge()

#enregistrer les donnees meteo dans la table info_meteo
def enregistrer_infos_meteo(ville, data, id_user, id_pays):
    if ville.lower() == "maroc":
        return

    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO info_meteo (ville, temp, vitesse_vent, date, desc, taux_hmdt, leve_sol, couche_sol, niv_mer, id_user, id_pays)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ville,
                data['main']['temp'],
                data['wind']['speed'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data['weather'][0]['description'],
                data['main']['humidity'],
                datetime.fromtimestamp(data['sys']['sunrise']).strftime("%H:%M:%S"),
                datetime.fromtimestamp(data['sys']['sunset']).strftime("%H:%M:%S"),
                data['main'].get('sea_level', 'N/A'),
                id_user,
                id_pays
            ))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'enregistrement des données météo: {e}")
        finally:
            conn.close()

#fonction appelee par main.py pour afficher accueil
def afficher_Accueil(grande_bordure, id_user):
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    direction_icone = DIRECTION_PROJET / "accessoires/grille"
    icone_hebdo = DIRECTION_PROJET / "accessoires/meteo_hebdo"

    API_KEY = 'VOTRE_CLE_ICI'  # Remplacez par votre clé API OpenWeatherMap

    #recuperer les donnees meteo d'aujourd'hui depuis le serveur api
    def obtenir_meteo(ville):
        url_weather = f'http://api.openweathermap.org/data/2.5/weather?q={ville}&appid={API_KEY}&units=metric&lang=fr'
        response = requests.get(url_weather)
        
        if response.status_code == 200:
            data = response.json()
            mise_a_jour_meteo(data)
            obtenir_previsions(ville)
            if ville.lower() != "maroc":
                code_pays = data['sys']['country']
                id_pays = id_pays_par_code(code_pays)
                if id_pays is not None:
                    enregistrer_infos_meteo(ville, data, id_user, id_pays)
                else:
                    print(f"Erreur: Identifiant du pays non trouvé pour le code {code_pays}")
        else:
            print(f"Erreur: {response.status_code}")

    #recuperer les donnees meteo des 6 prochains jours depuis le serveur api
    def obtenir_previsions(ville):
        url_forecast = f'http://api.openweathermap.org/data/2.5/forecast?q={ville}&appid={API_KEY}&units=metric&lang=fr'
        response = requests.get(url_forecast)
        
        if response.status_code == 200:
            data = response.json()
            mise_a_jour_previsions(data)
        else:
            print(f"Erreur: {response.status_code}")

    #remplacer les donnees meteorologiques actuelles par les nouvelles donnees recuperees
    def mise_a_jour_meteo(data):
        nom_ville.configure(text=f"{data['name']}")
        date_du_jour.configure(text=datetime.now().strftime("%A, %d %B %Y"))
        texte_temperature_actuelle.configure(text=f"{data['main']['temp']}°C")
        icone_actuelle_path = icone_hebdo / f"{data['weather'][0]['icon']}.png"
        icone_actuelle = ctk.CTkImage(Image.open(icone_actuelle_path), size=(100, 100))
        label_icone_actuelle.configure(image=icone_actuelle)
        label_icone_actuelle.image = icone_actuelle

        code_pays = data['sys']['country']
        nom_pays = nom_pays_par_code(code_pays)
        description_temps.configure(text=nom_pays)

        #remplacer les donnees meteorologiques actuelles aussi dans les description
        #en bas a droite de accueil par les nouvelles donnees recuperees
        mise_a_jour_infos(data)

    #remplacer les donnees meteorologiques des,6 prochains jours par les nouvelles donnees recuperees
    def mise_a_jour_previsions(data):
        global previsions_data
        previsions_data = data

        for widget in cadre_6.winfo_children():
            widget.destroy()

        jours_semaine = []
        temperatures_max = []
        temperatures_min = []
        icones_max = []
        icones_min = []

        total_entries = len(data['list'])
        nombre_de_jours = total_entries // 8

        for i in range(0, min(6, nombre_de_jours + 1)):
            index = i * 8
            if index >= total_entries:
                break

            jour_data = data['list'][index:index + 8]

            jour_timestamp = jour_data[0]['dt']
            jour = datetime.fromtimestamp(jour_timestamp).strftime("%A")

            temp_max = max(j['main']['temp_max'] for j in jour_data)
            temp_min = min(j['main']['temp_min'] for j in jour_data)
            
            icone_max = next(j['weather'][0]['icon'] for j in jour_data if j['main']['temp_max'] == temp_max)
            icone_min = next(j['weather'][0]['icon'] for j in jour_data if j['main']['temp_min'] == temp_min)

            jours_semaine.append(jour)
            temperatures_max.append(temp_max)
            temperatures_min.append(temp_min)
            icones_max.append(icone_max)
            icones_min.append(icone_min)

            bloc_jour = ctk.CTkFrame(cadre_6, corner_radius=20, fg_color="black")
            bloc_jour.pack(side="top", fill="x", padx=10, pady=(10,5), ipady=8)

            label_jour = ctk.CTkLabel(bloc_jour, text=jours_semaine[-1], fg_color="transparent", text_color="#ffffff")
            label_jour.pack(side="left", padx=(10, 0))

            cadre_icones = ctk.CTkFrame(bloc_jour, fg_color="transparent")
            cadre_icones.pack(side="right", padx=(10, 10))

            icone_min_img = ctk.CTkImage(Image.open(icone_hebdo / f"{icones_min[-1]}.png"), size=(30, 30))
            label_icone_min = ctk.CTkLabel(cadre_icones, image=icone_min_img, text="", fg_color="transparent")
            label_icone_min.image = icone_min_img
            label_icone_min.pack(side="left", padx=(0, 3))

            icone_max_img = ctk.CTkImage(Image.open(icone_hebdo / f"{icones_max[-1]}.png"), size=(30, 30))
            label_icone_max = ctk.CTkLabel(cadre_icones, image=icone_max_img, text="", fg_color="transparent")
            label_icone_max.image = icone_max_img
            label_icone_max.pack(side="left")

            label_temp_min = ctk.CTkLabel(cadre_icones, text=f"{temperatures_min[-1]}°C  ", fg_color="transparent", text_color="#ffffff")
            label_temp_min.pack(side="left", padx=(40, 0))

            label_temp_max = ctk.CTkLabel(cadre_icones, text=f"{temperatures_max[-1]}°C", fg_color="transparent", text_color="#ffffff")
            label_temp_max.pack(side="left", padx=(0, 5))

            label_jour.bind("<Enter>", lambda e: e.widget.configure(cursor="hand2"))
            label_jour.bind("<Leave>", lambda e: e.widget.configure(cursor=""))
            label_jour.bind("<Button-1>", lambda e, index=i, jour=jour: actualiser_horaire(index, jour))

        position_ville(data['city']['name'], data['city']['coord']['lat'], data['city']['coord']['lon'])
        mise_a_jour_horaire(data['list'][:8], jours_semaine[0])

    def actualiser_horaire(index, jour):
        jour_data = previsions_data['list'][index * 8:index * 8 + 8]
        mise_a_jour_horaire(jour_data, jour)

    def position_ville(ville, lat, lon):
        map_view.set_position(lat, lon)

    def mise_a_jour_horaire(jour_data, nom_du_jour):
        for widget in cadre_horaire.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            cadre_horaire,
            text=f"HORAIRES — {nom_du_jour.upper()}",
            font=("Georgia", 13, "bold"), text_color="#4f8ef7"
        ).pack(anchor="w", padx=15, pady=(12, 8))

        cadre_blocs = ctk.CTkFrame(cadre_horaire, fg_color="transparent")
        cadre_blocs.pack(fill="x", padx=10, pady=(0, 10))

        for horaire_data in jour_data:
            heure = datetime.strptime(horaire_data['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")

            bloc_horaire = ctk.CTkFrame(cadre_blocs, corner_radius=15, fg_color="#252a3d", width=95)
            bloc_horaire.pack(side="left", fill="y", padx=5, pady=5, ipadx=5, ipady=8)

            ctk.CTkLabel(
                bloc_horaire, text=heure,
                font=("Georgia", 15, "bold"), text_color="#4f8ef7"
            ).pack(anchor="center", pady=(10, 4))

            icone_horaire = ctk.CTkImage(
                Image.open(icone_hebdo / f"{horaire_data['weather'][0]['icon']}.png"), size=(45, 45)
            )
            label_icone_horaire = ctk.CTkLabel(bloc_horaire, image=icone_horaire, text="", fg_color="transparent")
            label_icone_horaire.image = icone_horaire
            label_icone_horaire.pack(pady=(0, 4))

            ctk.CTkLabel(
                bloc_horaire,
                text=f"{horaire_data['main']['temp']}°C",
                font=("Georgia", 13), text_color="#e8eaf6"
            ).pack(anchor="center", pady=(0, 10))

    def mise_a_jour_infos(data):
        for widget in cadre_info.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            cadre_info, text="DESCRIPTION MÉTÉO ACTUELLE",
            font=("Georgia", 13, "bold"), text_color="#4f8ef7"
        ).grid(row=0, column=0, columnspan=4, padx=15, pady=(12, 8), sticky="w")

        infos = [
            ("🌤  Description",    data['weather'][0]['description']),
            ("🌅  Lever soleil",   datetime.fromtimestamp(data['sys']['sunrise']).strftime("%H:%M")),
            ("🌇  Coucher soleil", datetime.fromtimestamp(data['sys']['sunset']).strftime("%H:%M")),
            ("💧  Humidité",       f"{data['main']['humidity']}%"),
            ("🌊  Niveau de mer",  data['main'].get('sea_level', 'N/A')),
            ("🌍  Pays",           nom_pays_par_code(data['sys']['country'])),
            ("💨  Vent",           f"{data['wind']['speed']} m/s"),
            ("🧭  Direction",      f"{data['wind']['deg']}°")
        ]

        for i, (titre, valeur) in enumerate(infos):
            bloc_info = ctk.CTkFrame(cadre_info, width=132, height=72, fg_color="#252a3d", corner_radius=12)
            bloc_info.grid(row=(i // 4) + 1, column=i % 4, padx=8, pady=(0, 10))
            bloc_info.grid_propagate(False)

            ctk.CTkLabel(
                bloc_info, text=titre, width=120,
                font=("Georgia", 11), text_color="#8892b0"
            ).pack(side="top", pady=(8, 2))

            ctk.CTkLabel(
                bloc_info, text=valeur, width=120,
                font=("Georgia", 13, "bold"), text_color="#e8eaf6"
            ).pack(side="bottom", pady=(2, 8))

    # ── COULEURS ──────────────────────────────────────────────────────
    FOND        = "#0f1117"
    CARTE       = "#1a1d27"
    CARTE2      = "#1e2235"
    ACCENT      = "#4f8ef7"
    TEXTE       = "#e8eaf6"
    TEXTE_DOUX  = "#8892b0"
    BLOC        = "#252a3d"
    BORDURE     = "#2a2f45"

    grande_bordure.configure(fg_color=FOND)

    # ── BARRE DE RECHERCHE ────────────────────────────────────────────
    zone_recherche = ctk.CTkFrame(grande_bordure, fg_color="transparent")
    zone_recherche.pack(side="top", anchor="center", padx=20, pady=(20, 10))

    champ_recherche = ctk.CTkEntry(
        zone_recherche,
        fg_color=CARTE, border_color=ACCENT,
        text_color=TEXTE,
        placeholder_text="  Rechercher une ville...",
        placeholder_text_color=TEXTE_DOUX,
        width=480, height=45, corner_radius=25,
        font=("Georgia", 14)
    )
    champ_recherche.pack(side="left", padx=(0, 10))

    icone_recherche = ctk.CTkImage(Image.open(direction_icone / "chercher.png"), size=(18, 18))
    button_recherche = ctk.CTkButton(
        zone_recherche,
        image=icone_recherche, text="Rechercher",
        command=lambda: obtenir_meteo(champ_recherche.get() or "maroc"),
        corner_radius=25,
        fg_color=ACCENT, hover_color="#3a6fd8",
        text_color="#ffffff",
        font=("Georgia", 13, "bold"),
        width=140, height=45
    )
    button_recherche.pack(side="left")

    # ── LIGNE 1 : MÉTÉO ACTUELLE + PRÉVISIONS + CARTE ─────────────────
    conteneur_superieur = ctk.CTkFrame(grande_bordure, fg_color="transparent")
    conteneur_superieur.pack(side="top", fill="x", padx=15, pady=(5, 5))

    # — Météo actuelle —
    cadre_meteo_actuelle = ctk.CTkFrame(
        conteneur_superieur, corner_radius=20,
        fg_color=CARTE, border_width=1, border_color=BORDURE
    )
    cadre_meteo_actuelle.pack(side="left", padx=(0, 10), pady=0, fill="y")

    cadre_textes = ctk.CTkFrame(cadre_meteo_actuelle, fg_color="transparent")
    cadre_textes.pack(padx=15, pady=10, fill="both")

    texte_meteo_actuelle = ctk.CTkLabel(
        cadre_textes, text="MÉTÉO ACTUELLE",
        font=("Georgia", 11, "bold"), text_color=ACCENT
    )
    texte_meteo_actuelle.pack(anchor="w", pady=(5, 2))

    nom_ville = ctk.CTkLabel(
        cadre_textes, text="Nom de la ville",
        font=("Georgia", 22, "bold"), text_color=TEXTE
    )
    nom_ville.pack(anchor="w")

    date_du_jour = ctk.CTkLabel(
        cadre_textes, text="",
        font=("Georgia", 12), text_color=TEXTE_DOUX
    )
    date_du_jour.pack(anchor="w", pady=(0, 8))

    texte_temperature_actuelle = ctk.CTkLabel(
        cadre_textes, text="--°C",
        font=("Georgia", 55, "bold"), text_color=TEXTE
    )
    texte_temperature_actuelle.pack(anchor="w")

    cadre_icone_desc = ctk.CTkFrame(cadre_textes, fg_color="transparent")
    cadre_icone_desc.pack(anchor="w", pady=(5, 5))

    icone_actuelle = ctk.CTkImage(Image.open(icone_hebdo / "01d.png"), size=(75, 75))
    label_icone_actuelle = ctk.CTkLabel(cadre_icone_desc, image=icone_actuelle, text="", fg_color="transparent")
    label_icone_actuelle.image = icone_actuelle
    label_icone_actuelle.pack(side="left")

    description_temps = ctk.CTkLabel(
        cadre_icone_desc, text="Pays",
        font=("Georgia", 14), text_color=TEXTE_DOUX
    )
    description_temps.pack(side="left", padx=(10, 0))

    # — Prévisions 6 jours —
    cadre_6 = ctk.CTkFrame(
        conteneur_superieur, corner_radius=20,
        fg_color=CARTE, border_width=1, border_color=BORDURE, width=190
    )
    cadre_6.pack(side="left", padx=(0, 10), pady=0, fill="y")

    ctk.CTkLabel(
        cadre_6, text="PRÉVISIONS 6 JOURS",
        font=("Georgia", 11, "bold"), text_color=ACCENT
    ).pack(anchor="w", padx=15, pady=(12, 5))

    # — Carte interactive —
    cadre_carte = ctk.CTkFrame(
        conteneur_superieur, corner_radius=20,
        fg_color=CARTE, border_width=1, border_color=BORDURE
    )
    cadre_carte.pack(side="left", fill="both", expand=True)

    ctk.CTkLabel(
        cadre_carte, text="LOCALISATION",
        font=("Georgia", 11, "bold"), text_color=ACCENT
    ).pack(anchor="w", padx=15, pady=(12, 5))

    map_view = tkintermapview.TkinterMapView(cadre_carte, width=510, height=235, corner_radius=15)
    map_view.set_position(48.8566, 2.3522)
    map_view.set_zoom(6)
    map_view.pack(padx=10, pady=(0, 10))

    # ── LIGNE 2 : HORAIRES + DESCRIPTION ─────────────────────────────
    conteneur_inferieur = ctk.CTkFrame(grande_bordure, fg_color="transparent")
    conteneur_inferieur.pack(side="top", fill="x", padx=15, pady=(5, 10))

    cadre_horaire = ctk.CTkFrame(
        conteneur_inferieur, corner_radius=20,
        fg_color=CARTE, border_width=1, border_color=BORDURE
    )
    cadre_horaire.pack(side="left", fill="both", expand=True, padx=(0, 10))

    cadre_info = ctk.CTkFrame(
        conteneur_inferieur, corner_radius=20,
        fg_color=CARTE, border_width=1, border_color=BORDURE, width=580
    )
    cadre_info.pack(side="right", fill="both")

    obtenir_meteo("maroc")