from flask import Flask, render_template, request, url_for, redirect, flash, session
from werkzeug.utils import secure_filename
import os
from auth import auth as auth_blueprint
from models import db, Project
from forums import forums

app = Flask(__name__, template_folder='templates')
app.secret_key = 'apikey'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(forums, url_prefix='/forums')

db.init_app(app)

# Context processor to make session data available in all templates
@app.context_processor
def inject_user():
    username = session.get('username')
    return dict(username=username)

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/')
def home():
    return render_template('acceuil.html')

@app.route('/acceuil')
def accueil():
    return render_template('acceuil.html')

@app.route('/forum')
def forum():
    return render_template('forum.html')

@app.route('/devlog')
def devlog():
    return render_template('devlog.html')

@app.route('/industrie')
def industrie():
    return render_template('industrie.html')

@app.route('/connexion')
def connexion():
    return render_template('connexion.html')

@app.route('/inscription')
def inscription():
    return render_template('inscription.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/quiz1')
def quiz1():
    return render_template('quiz1.html')

@app.route('/quiz2')
def quiz2():
    return render_template('quiz2.html')

@app.route('/quiz3')
def quiz3():
    return render_template('quiz3.html')

@app.route('/businesscase')
def businesscase():
    return render_template('businesscase.html')

@app.route('/businesscase1')
def businesscase1():
    return render_template('businesscase1.html')

@app.route('/businesscase2')
def businesscase2():
    return render_template('businesscase2.html')

@app.route('/businesscase3')
def businesscase3():
    return render_template('businesscase3.html')

@app.route('/energie', methods=['GET', 'POST'])
def energie():
    if request.method == 'POST':
        if 'file-upload' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        file = request.files['file-upload']
        full_name = request.form['full-name']
        project_title = request.form['project-title']

        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)

        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                pdf_text = extract_text_from_pdf(filepath)
                case_study = ai_generate_case_study(pdf_text)
                
                project_id = len(projects)
                project = {
                    'id': project_id,
                    'title': project_title,
                    'full_name': full_name,
                    'file_path': filename,
                    'case_study': case_study
                }
                projects.append(project)
                
                flash('Étude de cas générée avec succès', 'success')
                return redirect(url_for('energie'))
            except Exception as e:
                flash(f'Erreur lors du traitement du fichier : {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Veuillez télécharger un fichier PDF valide.', 'error')
            return redirect(request.url)
    
    return render_template('energie.html', projects=projects)

@app.route('/casia/<int:project_id>')
def casia(project_id):
    if project_id < len(projects):
        case_study = projects[project_id]['case_study']
        return render_template('casia.html', case_study=case_study)
    else:
        flash("Projet non trouvé", 'error')
        return redirect(url_for('energie'))

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    global projects
    if project_id < len(projects):
        del projects[project_id]
        # Re-index the remaining projects
        for i in range(len(projects)):
            projects[i]['id'] = i
        flash('Projet supprimé avec succès', 'success')
    else:
        flash('Projet non trouvé', 'error')
    return redirect(url_for('energie'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
