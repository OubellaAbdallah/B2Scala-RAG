# Ce script Python recherche tous les fichiers .scala dans le répertoire courant et en copie le contenu dans des fichiers .txt.

import os

# Obtenez le répertoire de travail actuel
repertoire_courant = os.getcwd()

# Parcourez tous les fichiers dans le répertoire
for nom_fichier in os.listdir(repertoire_courant):
    # Vérifiez si le fichier se termine par .scala
    if nom_fichier.endswith(".scala"):
        chemin_scala = os.path.join(repertoire_courant, nom_fichier)

        # Créez le nom du fichier de destination avec l'extension .txt
        nom_base = os.path.splitext(nom_fichier)[0]
        nom_txt = nom_base + ".txt"
        chemin_txt = os.path.join(repertoire_courant, nom_txt)

        try:
            # Ouvrez le fichier .scala en mode lecture
            with open(chemin_scala, 'r', encoding='utf-8') as fichier_scala:
                contenu = fichier_scala.read()

            # Ouvrez le fichier .txt en mode écriture
            with open(chemin_txt, 'w', encoding='utf-8') as fichier_txt:
                fichier_txt.write(contenu)

            print(f"Le contenu de '{nom_fichier}' a été copié dans '{nom_txt}'.")

        except Exception as e:
            print(f"Une erreur est survenue lors du traitement de '{nom_fichier}': {e}")

print("Opération terminée.")
