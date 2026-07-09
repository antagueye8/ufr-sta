import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ---------- CONFIGURATION SENSIBLE (variables d'environnement) ----------
# En développement, si les variables d'environnement ne sont pas définies,
# des valeurs de secours sont utilisées (uniquement pour pouvoir lancer le
# projet immédiatement). En production, définis SECRET_KEY, ADMIN_USERNAME
# et ADMIN_PASSWORD_HASH dans un fichier .env (jamais commité sur GitHub).

app.secret_key = os.environ.get('SECRET_KEY', 'cle-de-secours-developpement-uniquement')

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
# Hash de secours correspondant au mot de passe "ufrsta2026" (à changer en prod
# via la variable d'environnement ADMIN_PASSWORD_HASH)
ADMIN_PASSWORD_HASH = os.environ.get(
    'ADMIN_PASSWORD_HASH',
    'scrypt:32768:8:1$x9zM09F34Xp9GIan$8a0219dfa7c610035171e2943d4fb30f24ea1ac09f3757116115db247c86c24495b9d1afc7e9f48b5326b640b098bee533eb8e6eb71ae11a40c80605594332a5'
)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database', 'ufrsta.db').replace('\\', '/')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
db = SQLAlchemy(app)


class Actualite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(200), nullable=True)


class Activite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    lieu = db.Column(db.String(200), nullable=False)
    organisateur = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photos = db.relationship('ActivitePhoto', backref='activite', cascade='all, delete-orphan')


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(50), nullable=False)
    photos = db.relationship('AlbumPhoto', backref='album', cascade='all, delete-orphan')

    @property
    def cover(self):
        return self.photos[0].filename if self.photos else None
    @property
    def count(self):
        return len(self.photos)

class ActivitePhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    activite_id = db.Column(db.Integer, db.ForeignKey('activite.id'), nullable=False)

class AlbumPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    sujet = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)
    lu = db.Column(db.Boolean, default=False)

class Formation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    niveau = db.Column(db.String(200), nullable=False)
    duree = db.Column(db.String(100), nullable=False)
    admission = db.Column(db.String(300), nullable=False)
    debouches = db.Column(db.String(300), nullable=False)
    modules_s1 = db.Column(db.String(500), nullable=False, default='')
    modules_s2 = db.Column(db.String(500), nullable=False, default='')

    @property
    def programme(self):
        return {
            "Semestre 1": [m.strip() for m in self.modules_s1.split(',') if m.strip()],
            "Semestre 2": [m.strip() for m in self.modules_s2.split(',') if m.strip()],
        }

# ---------- SECURITE ADMIN ----------

def connexion_requise(f):
    @wraps(f)
    def fonction_protegee(*args, **kwargs):
        if not session.get('admin_connecte'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return fonction_protegee


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_connecte'] = True
            return redirect(url_for('admin_actualites'))
        else:
            return render_template('admin/login.html', erreur="Identifiants incorrects")

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_connecte', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@connexion_requise
def admin_dashboard():
    return render_template('admin/dashboard.html',
                           nb_actualites=Actualite.query.count(),
                           nb_activites=Activite.query.count(),
                           nb_albums=Album.query.count(),
                           nb_formations=Formation.query.count(),
                           nb_messages=Message.query.count(),
                           nb_messages_non_lus=Message.query.filter_by(lu=False).count())

# ---------- PAGES PUBLIQUES ----------

@app.route('/')
def accueil():
    dernieres_actualites = Actualite.query.order_by(Actualite.id.desc()).limit(3).all()
    return render_template('index.html', actualites=dernieres_actualites, active_page='accueil')


@app.route('/departements')
def departements():
        liste_departements = [
        {
            "nom": "Département Informatique",
            "description": "Formation en développement logiciel, cybersécurité et intelligence artificielle.",
            "responsable": "Pr. Amadou Dahirou Gueye",
            "contact": "dahirou.gueye@uam.edu.sn"
        },
        {
            "nom": "Département Mathématiques",
            "description": "Formation en mathématiques fondamentales et appliquées.",
            "responsable": "Dr. Sow",
            "contact": "chef-departement-mim@uam.edu.sn"
        },
        {
            "nom": "Département Physique",
            "description": "Filiére  Physique et Applications.",
            "responsable": "Dr. Ndao",
            "contact": "chef-departement-smu@uam.edu.sn"
        }
    ]
        return render_template('departements.html', departements=liste_departements, active_page='departements')


@app.route('/formations')
def formations():
    liste_formations = Formation.query.order_by(Formation.id).all()
    return render_template('formations.html', formations=liste_formations, active_page='formations')


@app.route('/actualites')
def actualites():
    toutes_actualites = Actualite.query.order_by(Actualite.id).all()
    return render_template('actualites.html', actualites=toutes_actualites, active_page='actualites')


@app.route('/activites')
def activites():
    toutes_activites = Activite.query.order_by(Activite.id).all()
    return render_template('activites.html', activites=toutes_activites, active_page='activites')


@app.route('/galerie')
def galerie():
    tous_albums = Album.query.order_by(Album.id.desc()).all()
    return render_template('galerie.html', albums=tous_albums, active_page='galerie')


@app.route('/enseignants')
def enseignants():
    liste_enseignants = [
        {
            "nom": "Dr. Sow",
            "grade": "Maître de Conférences Titulaire - Enseignant-chercheur",
            "departement": "Mathématiques",
            "email": "thierno.sow@uam.edu.sn",
            "recherche": "Analyse non linéaire, Géométrie des Espaces",
            "photo": "sow.jpg"
        },
        {
            "nom": "Pr. Amadou Dahirou Gueye",
            "grade": "Professeur Titulaire - Enseignant-chercheur en Informatique",
            "departement": "Informatique",
            "email": "dahirou.gueye@uam.edu.sn",
            "recherche": "Intelligence artificielle",
            "photo": "adg.jpg"
        },
        {
            "nom": "Dr. Makha Ndao",
            "grade": "Maître de Conférences Titulaire - Enseignant-chercheur",
            "departement": "Physique",
            "email": "makha.ndao@uam.edu.sn",
            "recherche": "Milieux denses et matériaux",
            "photo": "makha.jpg"
        }
    ]
    return render_template('enseignants.html', enseignants=liste_enseignants, active_page='enseignants')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    envoye= False
    if request.method == 'POST':
        #Traitement du formulaire
        nom = request.form.get('nom')
        email = request.form.get('email')
        sujet = request.form.get('sujet')
        message = request.form.get('message')
        envoye = True
    return render_template('contact.html', envoye=envoye)



# ---------- ADMIN ACTUALITES ----------

@app.route('/admin/actualites')
@connexion_requise
def admin_actualites():
    toutes_actualites = Actualite.query.order_by(Actualite.id.desc()).all()
    return render_template('admin/actualites_liste.html', actualites=toutes_actualites)


@app.route('/admin/actualites/ajouter', methods=['GET', 'POST'])
@connexion_requise
def admin_ajouter_actualite():
    if request.method == 'POST':
        titre = request.form['titre']
        date = request.form['date']
        description = request.form['description']
        photo = request.form.get('photo', '')

        nouvelle_actualite = Actualite(titre=titre, date=date, description=description, photo=photo)
        db.session.add(nouvelle_actualite)
        db.session.commit()

        return redirect(url_for('admin_actualites'))

    return render_template('admin/actualite_form.html')


@app.route('/admin/actualites/modifier/<int:id>', methods=['GET', 'POST'])
@connexion_requise
def admin_modifier_actualite(id):
    actualite = Actualite.query.get_or_404(id)

    if request.method == 'POST':
        actualite.titre = request.form['titre']
        actualite.date = request.form['date']
        actualite.description = request.form['description']
        actualite.photo = request.form.get('photo', '')

        db.session.commit()
        return redirect(url_for('admin_actualites'))

    return render_template('admin/actualite_form.html', actualite=actualite)


@app.route('/admin/actualites/supprimer/<int:id>')
@connexion_requise
def admin_supprimer_actualite(id):
    actualite = Actualite.query.get_or_404(id)
    db.session.delete(actualite)
    db.session.commit()
    return redirect(url_for('admin_actualites'))


# ---------- ADMIN ACTIVITES ----------

@app.route('/admin/activites')
@connexion_requise
def admin_activites():
    toutes_activites = Activite.query.order_by(Activite.id.desc()).all()
    return render_template('admin/activites_liste.html', activites=toutes_activites)


@app.route('/admin/activites/ajouter', methods=['GET', 'POST'])
@connexion_requise
def admin_ajouter_activite():
    if request.method == 'POST':
        titre = request.form['titre']
        date = request.form['date']
        lieu = request.form['lieu']
        organisateur = request.form['organisateur']
        description = request.form['description']
        photos_brutes = request.form.get('photos', '')

        nouvelle_activite = Activite(
            titre=titre, date=date, lieu=lieu, organisateur=organisateur,
            description=description, 
        )
        for nom_fichier in [p.strip() for p in photos_brutes.split(',') if p.strip()]:
            nouvelle_activite.photos.append(ActivitePhoto(filename=nom_fichier))
        db.session.add(nouvelle_activite)
        db.session.commit()

        return redirect(url_for('admin_activites'))

    return render_template('admin/activite_form.html')


@app.route('/admin/activites/modifier/<int:id>', methods=['GET', 'POST'])
@connexion_requise
def admin_modifier_activite(id):
    activite = Activite.query.get_or_404(id)

    if request.method == 'POST':
        activite.titre = request.form['titre']
        activite.date = request.form['date']
        activite.lieu = request.form['lieu']
        activite.organisateur = request.form['organisateur']
        activite.description = request.form['description']
        
        ActivitePhoto.query.filter_by(activite_id=activite.id).delete()
        photos_brutes = request.form.get('photos', '')
        for nom_fichier in [p.strip() for p in photos_brutes.split(',') if p.strip()]:
            activite.photos.append(ActivitePhoto(filename=nom_fichier))
        db.session.commit()
        return redirect(url_for('admin_activites'))

    return render_template('admin/activite_form.html', activite=activite)


@app.route('/admin/activites/supprimer/<int:id>')
@connexion_requise
def admin_supprimer_activite(id):
    activite = Activite.query.get_or_404(id)
    db.session.delete(activite)
    db.session.commit()
    return redirect(url_for('admin_activites'))


# ---------- ADMIN GALERIE ----------

@app.route('/admin/galerie')
@connexion_requise
def admin_galerie():
    tous_albums = Album.query.all()
    return render_template('admin/galerie_liste.html', albums=tous_albums)


@app.route('/admin/galerie/ajouter', methods=['GET', 'POST'])
@connexion_requise
def admin_ajouter_album():
    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        date = request.form['date']
        photos_brutes = request.form.get('photos', '')

        nouvel_album = Album(titre=titre, description=description, date=date)
        for nom_fichier in [p.strip() for p in photos_brutes.split(',') if p.strip()]:
            nouvel_album.photos.append(AlbumPhoto(filename=nom_fichier))
        db.session.add(nouvel_album)
        db.session.commit()

        return redirect(url_for('admin_galerie'))

    return render_template('admin/album_form.html')

@app.route('/admin/galerie/photo/supprimer/<int:id>', methods=['POST'])
@connexion_requise
def admin_supprimer_photo(id):
    photo = AlbumPhoto.query.get_or_404(id)
    db.session.delete(photo)
    db.session.commit()
    return redirect(url_for('admin_galerie'))


@app.route('/admin/galerie/supprimer/<int:id>')
@connexion_requise
def admin_supprimer_album(id):
    album = Album.query.get_or_404(id)
    db.session.delete(album)
    db.session.commit()
    return redirect(url_for('admin_galerie'))

# ==================== ADMIN : MESSAGES DE CONTACT ====================

@app.route('/admin/messages')
@connexion_requise
def admin_messages():
    tous_messages = Message.query.order_by(Message.date_envoi.desc()).all()
    return render_template('admin/messages_liste.html', messages=tous_messages)


@app.route('/admin/messages/lu/<int:id>', methods=['POST'])
@connexion_requise
def admin_marquer_lu(id):
    message = Message.query.get_or_404(id)
    message.lu = not message.lu
    db.session.commit()
    return redirect(url_for('admin_messages'))


@app.route('/admin/messages/supprimer/<int:id>', methods=['POST'])
@connexion_requise
def admin_supprimer_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for('admin_messages'))


# ==================== ADMIN : FORMATIONS ====================

@app.route('/admin/formations')
@connexion_requise
def admin_formations():
    toutes_formations = Formation.query.order_by(Formation.id).all()
    return render_template('admin/formations_liste.html', formations=toutes_formations)


@app.route('/admin/formations/ajouter', methods=['GET', 'POST'])
@connexion_requise
def admin_ajouter_formation():
    if request.method == 'POST':
        nouvelle_formation = Formation(
            nom=request.form['nom'],
            niveau=request.form['niveau'],
            duree=request.form['duree'],
            admission=request.form['admission'],
            debouches=request.form['debouches'],
            modules_s1=request.form.get('modules_s1', ''),
            modules_s2=request.form.get('modules_s2', '')
        )
        db.session.add(nouvelle_formation)
        db.session.commit()
        return redirect(url_for('admin_formations'))
    return render_template('admin/formation_form.html', formation=None)


@app.route('/admin/formations/modifier/<int:id>', methods=['GET', 'POST'])
@connexion_requise
def admin_modifier_formation(id):
    formation = Formation.query.get_or_404(id)
    if request.method == 'POST':
        formation.nom = request.form['nom']
        formation.niveau = request.form['niveau']
        formation.duree = request.form['duree']
        formation.admission = request.form['admission']
        formation.debouches = request.form['debouches']
        formation.modules_s1 = request.form.get('modules_s1', '')
        formation.modules_s2 = request.form.get('modules_s2', '')
        db.session.commit()
        return redirect(url_for('admin_formations'))
    return render_template('admin/formation_form.html', formation=formation)


@app.route('/admin/formations/supprimer/<int:id>', methods=['POST'])
@connexion_requise
def admin_supprimer_formation(id):
    formation = Formation.query.get_or_404(id)
    db.session.delete(formation)
    db.session.commit()
    return redirect(url_for('admin_formations'))


if __name__ == '__main__':
    app.run(debug=True)