import os
from app import app, db

# S'assurer que le dossier database existe
basedir = os.path.abspath(os.path.dirname(__file__))
db_folder = os.path.join(basedir, 'database')
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

with app.app_context():
    db.create_all()
    print("Base de données créée avec succès !")