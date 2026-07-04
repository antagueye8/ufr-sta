import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
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

@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/departements')
def departements():
    liste_departements = [
        {
            "nom": "Département Informatique",
            "description": "Formation en développement logiciel, réseaux et cybersécurité.",
            "responsable": "Dr. Diallo",
            "contact": "info@ufrsta.sn"
        },
        {
            "nom": "Département Mathématiques",
            "description": "Formation en mathématiques fondamentales et appliquées.",
            "responsable": "Dr. Ndiaye",
            "contact": "maths@ufrsta.sn"
        },
        {
            "nom": "Département Physique",
            "description": "Formation en physique théorique et expérimentale.",
            "responsable": "Dr. Sow",
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
@app.route('/admin/actualites')
def admin_actualites():
    toutes_actualites = Actualite.query.all()
    return render_template('admin/actualites_liste.html', actualites=toutes_actualites)

@app.route('/admin/actualites/ajouter', methods=['GET', 'POST'])
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
@app.route('/actualites')
def actualites():
    toutes_actualites = Actualite.query.all()
    return render_template('actualites.html', actualites=toutes_actualites)

if __name__ == '__main__':
    app.run(debug=True)