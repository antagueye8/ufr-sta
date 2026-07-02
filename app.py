from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)