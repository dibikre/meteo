#import sys
#sys.path.append(r"c:\\users\\dibi\\appdata\\local\\packages\\pythonsoftwarefoundation.python.3.13_qbz5n2kfra8p0\\localcache\\local-packages\\python313\\site-packages")
import sqlite3
import locale
from pathlib import Path

# Définir le chemin du projet
DIRECTION_PROJET = Path(__file__).parent
CHEMIN_DB = DIRECTION_PROJET / "db/BASE_DE_DONNEES.db"

def connect_db():
    """Connecte à la base de données SQLite et retourne la connexion."""
    try:
        return sqlite3.connect(CHEMIN_DB)
    except sqlite3.Error as e:
        print(f"Erreur lors de la connexion à la base de données: {e}")
        return None

def horloge():
    """Configure la locale pour l'affichage des dates en français."""
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error as e:
        print(f"Erreur de configuration de la locale: {e}. Utilisation de la locale par défaut.")
        locale.setlocale(locale.LC_TIME, '')

def id_pays_par_code(code):
    """Retourne l'ID du pays depuis la base de données en fonction de son code."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_pays FROM tab_pays WHERE code = ?", (code,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de l'ID du pays: {e}")
            return None
        finally:
            conn.close()

def nom_pays_par_code(code):
    """Retourne le nom du pays depuis la base de données en fonction de son code."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT nom_pays FROM tab_pays WHERE code = ?", (code,))
            result = cursor.fetchone()
            return result[0] if result else "Inconnu"
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération du nom du pays: {e}")
            return "Inconnu"
        finally:
            conn.close()