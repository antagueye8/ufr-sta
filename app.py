import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'une_cle_secrete_a_changer'
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
    photos = db.Column(db.String(500), nullable=True)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(50), nullable=False)
    photos = db.relationship('Photo', backref='album', cascade='all, delete-orphan')


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_fichier = db.Column(db.String(200), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)


# ---------- SECURITE ADMIN ----------

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'ufrsta2026'


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

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_connecte'] = True
            return redirect(url_for('admin_actualites'))
        else:
            return render_template('admin/login.html', erreur="Identifiants incorrects")

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_connecte', None)
    return redirect(url_for('admin_login'))


# ---------- PAGES PUBLIQUES ----------

@app.route('/')
def accueil():
    dernieres_actualites = Actualite.query.order_by(Actualite.id.desc()).limit(3).all()
    return render_template('index.html', actualites=dernieres_actualites)

@app.route('/departements')
def departements():
    liste_departements = [
        {
            "nom": "Département Informatique",
            "description": "Formation en développement logiciel, réseaux et cybersécurité.",
            "responsable": "Dr. Gueye",
            "contact": "info@ufrsta.sn"
        },
        {
            "nom": "Département Mathématiques",
            "description": "Formation en mathématiques fondamentales et appliquées.",
            "responsable": "Dr. Sow",
            "contact": "maths@ufrsta.sn"
        },
        {
            "nom": "Département Physique",
            "description": "Formation en physique théorique et expérimentale.",
            "responsable": "Dr. Ndao",
            "contact": "physique@ufrsta.sn"
        }
    ]
    return render_template('departements.html', departements=liste_departements)


@app.route('/formations')
def formations():
    liste_formations = [
        {
            "nom": "Licence Informatique",
            "niveau": "Licence (Bac+3)",
            "duree": "3 ans",
            "admission": "Bac scientifique ou équivalent",
            "debouches": "Développeur, Administrateur systèmes, Analyste cybersécurité",
            "programme": {
                "Semestre 1": ["Algorithmique", "Python", "Logique", "Mathématiques"],
                "Semestre 2": ["POO", "Base de données", "Système d'Exploitation", "Cybersécurité"]
            }
        },
        {
            "nom": "Master Informatique",
            "niveau": "Master (Bac+5)",
            "duree": "2 ans",
            "admission": "Licence en Informatique ou équivalent",
            "debouches": "Ingénieur logiciel, Chef de projet IT, Chercheur",
            "programme": {
                "Semestre 1": ["Architectures avancées", "Cloud Computing", "IA"],
                "Semestre 2": ["Cybersécurité avancée", "Big Data", "Projet de recherche"]
            }
        }
    ]
    return render_template('formations.html', formations=liste_formations)


@app.route('/actualites')
def actualites():
    toutes_actualites = Actualite.query.all()
    return render_template('actualites.html', actualites=toutes_actualites)


@app.route('/activites')
def activites():
    toutes_activites = Activite.query.all()
    return render_template('activites.html', activites=toutes_activites)


@app.route('/galerie')
def galerie():
    tous_albums = Album.query.all()
    return render_template('galerie.html', albums=tous_albums)


# ---------- ADMIN ACTUALITES ----------

@app.route('/admin/actualites')
@connexion_requise
def admin_actualites():
    toutes_actualites = Actualite.query.all()
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
    toutes_activites = Activite.query.all()
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
        photos = request.form.get('photos', '')

        nouvelle_activite = Activite(titre=titre, date=date, lieu=lieu, organisateur=organisateur, description=description, photos=photos)
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
        activite.photos = request.form.get('photos', '')

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
        noms_photos = request.form.get('photos', '')

        nouvel_album = Album(titre=titre, description=description, date=date)
        db.session.add(nouvel_album)
        db.session.commit()

        if noms_photos:
            for nom in noms_photos.split(','):
                nom = nom.strip()
                if nom:
                    photo = Photo(nom_fichier=nom, album_id=nouvel_album.id)
                    db.session.add(photo)
            db.session.commit()

        return redirect(url_for('admin_galerie'))

    return render_template('admin/album_form.html')


@app.route('/admin/galerie/supprimer/<int:id>')
@connexion_requise
def admin_supprimer_album(id):
    album = Album.query.get_or_404(id)
    db.session.delete(album)
    db.session.commit()
    return redirect(url_for('admin_galerie'))


if __name__ == '__main__':
    app.run(debug=True)