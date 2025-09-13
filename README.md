# BeSoft — Site vitrine + Admin (sans dépendances)

## Lancer en local
```bash
python3 server.py
```
Puis ouvrez le navigateur sur http://localhost:8000

- Admin : http://localhost:8000/admin
- Identifiants par défaut : **admin / admin123**

## Déploiement (Render)
1. Poussez le contenu de ce dossier dans un dépôt GitHub (fichiers à la racine).
2. Créez un service *Web Service* sur Render connecté à ce dépôt.
3. Start command : `python server.py`
4. C’est tout !

_Aucune dépendance externe requise._