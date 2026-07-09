import os
from app import app, db, Actualite, Activite, ActivitePhoto, Album, AlbumPhoto, Formation

basedir = os.path.abspath(os.path.dirname(__file__))
db_folder = os.path.join(basedir, 'database')
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

with app.app_context():
    db.create_all()

    # Ne peupler que si les tables sont vides (pour ne pas dupliquer à chaque exécution)
    if Activite.query.count() == 0:
        activites_initiales = [
            {
                "titre": "Journée scientifique UFR STA",
                "date": "09 Mai 2026",
                "lieu": "Salle rectorat",
                "organisateur": "AESTA",
                "description": "Célebration du mérite académique, de l'engagement estudiantin et de la promotion universitaire !",
                "photos": ["images1.jpg", "images2.jpg", "images3.jpg"]
            },
            {
                "titre": "Journée internationale des gens de la mer",
                "date": "25 Juin 2026",
                "lieu": "Grand Théatre National",
                "organisateur": "ANAM",
                "description": "Les étudiants de l'UFR STA s'illustrent à la journée internationale des gens de mer !",
                "photos": ["images4.jpg", "images5.jpg"]
            },
            {
                "titre": "Mise en oeuvre de la continuité pédagogique à l'UAM",
                "date": "27 Juin 2026",
                "lieu": "Salle U9",
                "organisateur": "Direction de l'UFR STA",
                "description": "Digitalisation et excellence:l'UFR STA prete pour la continuité pédagogique en ligne !",
                "photos": ["actu1.jpg"]
            }
        ]
        for data in activites_initiales:
            act = Activite(titre=data["titre"], date=data["date"], lieu=data["lieu"],
                            organisateur=data["organisateur"], description=data["description"])
            for f in data["photos"]:
                act.photos.append(ActivitePhoto(filename=f))
            db.session.add(act)

    if Album.query.count() == 0:
        albums = [
            {
                "titre": "Journée scientifique",
                "description": "Retour en images sur la journée scientifique annuelle de l'UFR STA.",
                "date": "2026",
                "photos": ["images-1.jpg", "galerie-3.jpg", "galerie-4.jpg", "galerie-7.jpg", "galerie-8.jpg",
                           "galerie-9.jpg", "galerie-11.jpg", "galerie-12.jpg", "galerie-13.jpg"]
            },
            {
                "titre": "Passation de service",
                "description": "Ceremonie de Passation de service UFR STA.",
                "date": "2026",
                "photos": ["actu3.jpg", "galerie-2.jpg"]
            },
            {
                "titre": "Inauguration salle informatique",
                "description": "L'UFR STA a inauguré sa salle informatique avec des ordinateurs de dernières génération.",
                "date": "23-06-2026",
                "photos": ["Salle informatique.jpg", "galerie-14.jpg", "galerie-15.jpg", "galerie-16.jpg", "galerie-17.jpg"]
            }
        ]
        for data in albums:
            album = Album(titre=data["titre"], description=data["description"], date=data["date"])
            for f in data["photos"]:
                album.photos.append(AlbumPhoto(filename=f))
            db.session.add(album)

    if Actualite.query.count() == 0:
        actus_initiales = [
            {
                "titre": "Appel à candidature pour l'UFR STA",
                "date": "12 Mai 2026",
                "description": "L'Université Amadou Mahtar MBOW lance un appel à candidature pour le recrutement de deux Enseignants-Chercheurs au sein de l'UFR Science et Technologies Avancées.",
                "photo": "actu4.jpg"
            },
            {
                "titre": "Les mathématiques au service de la communauté",
                "date": "30 Avril 2026",
                "description": "L'UFR STA, à travers son Département Mathématiques, Informatique et modelisation (MIM) organise une conférence scientifique.",
                "photo": "actu5.jpg"
            }
        ]
        for data in actus_initiales:
            db.session.add(Actualite(**data))

    if Formation.query.count() == 0:
        formations_initiales = [
            {
                "nom": "Licence Informatique",
                "niveau": "Licence (Bac+3)",
                "duree": "3 ans",
                "admission": "Bac scientifique ou équivalent",
                "debouches": "Developpeur, Analyste cybersécurité, Administrateur système",
                "modules_s1": "Algorithmique, Python, Logique, Mathématiques",
                "modules_s2": "POO, Base de données, Système d'Exploitation, Cybersécurité"
            },
            {
                "nom": "Licence Mathématique",
                "niveau": "Licence (Bac+3)",
                "duree": "3 ans",
                "admission": "Bac scientifique ou équivalent",
                "debouches": "Enseignant, Actuaire, Chercheur",
                "modules_s1": "Algèbre 1, Analyse 1, Statistiques",
                "modules_s2": "Algèbre linéaire, Analyse numérique, Probabilités"
            },
            {
                "nom": "Licence Physique",
                "niveau": "Licence (Bac+3)",
                "duree": "3 ans",
                "admission": "Bac scientifique ou équivalent",
                "debouches": "Enseignant, Technicien de laboratoire, Chercheur",
                "modules_s1": "Mécanique du point, Electricité, Mathématiques, Optique",
                "modules_s2": "Thermodynamique, Electromagnétisme, Mécanique générale"
            }
        ]
        for data in formations_initiales:
            db.session.add(Formation(**data))

    db.session.commit()
    print("Base de données créée et peuplée avec succès !")
