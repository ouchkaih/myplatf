from flask import Flask, render_template, request, url_for, redirect, flash, session
from werkzeug.utils import secure_filename
import openai
import os
from auth import auth as auth_blueprint
from models import db, CaseStudy, Comment, User, Project
from forums import forums
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from ia import extract_text_from_pdf, generate_case_study as ai_generate_case_study , generate_quiz
from forms import CaseStudyCreationForm, CommentCreationForm
import tiktoken
from dotenv import load_dotenv

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import sqlalchemy.orm as so
load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv('OPENAI_API_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(forums, url_prefix='/forums')

db.init_app(app)
login_manager = LoginManager(app)
openai.api_key = os.getenv('OPENAI_API_KEY')


# Fonction pour compter les tokens
def count_tokens(messages, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for message in messages:
        num_tokens += len(encoding.encode(message["content"]))
    return num_tokens

# Fonction pour tronquer le texte
def truncate_text(text, max_tokens, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return encoding.decode(tokens)



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

@app.route('/quiz/<int:id>')
def quiz(id):
    if not current_user.is_authenticated:
        flash('Veuillez vous connecter', 'error')
    case_study = db.session.scalar(sa.select(Project).where(Project.id == id))

    return render_template('quiz.html', id=id, case_study=case_study)

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

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))


def get_all_projects():
    with app.app_context():
        return Project.query.all()

@app.route('/energie', methods=['GET', 'POST'])
def energie():

    projects = get_all_projects()
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

                # Save project details to the database
                new_project = Project(
                    title=project_title,
                    full_name=full_name,
                    file_path=filename,
                    case_study=case_study
                )
                db.session.add(new_project)
                db.session.commit()
                
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
    projects = get_all_projects()
    if 0 < len(projects):
        project = next((proj for proj in projects if proj.id == project_id), None)
        if project:
            case_study = project.case_study
            return render_template('casia.html', case_study=case_study)
        else:
            flash("Projet non trouvé", 'error')
            return redirect(url_for('energie'))
    else:
        flash("Aucun projet disponible", 'error')
        return redirect(url_for('energie'))

@app.route('/delete_project/<int:id>', methods=['POST'])
def delete_project(id):
    project = Project.query.get_or_404(id)
    # if project.author_id != current_user.id:
    #     flash('Vous ne pouvez pas supprimer ce projet.', 'error')
    #     return redirect(url_for('energie'))
    
    db.session.delete(project)
    db.session.commit()
    flash('Projet supprimé avec succès.', 'success')
    return redirect(url_for('energie'))



@app.route('/case-studies')
def case_studies():
    case_studies = CaseStudy.query.order_by(CaseStudy.date_posted)
    case_study_form = CaseStudyCreationForm()
    return render_template('case-studies.html', case_studies=case_studies, case_study_form=case_study_form, current_user=current_user)

@app.route('/create-case-study', methods=['POST'])
def create_case_study():
    if not current_user.is_authenticated:
        flash('Veuillez vous connecter', 'error')
        return redirect(url_for('login'))
    
    form = CaseStudyCreationForm()
    f = form.pdf_file.data
    filename = secure_filename(f.filename)
    path = os.path.join(app.instance_path, "uploads", filename)
    f.save(path)
    text = extract_text_from_pdf(path)
    content = ai_generate_case_study(text)
    study = CaseStudy(
        title=form.title.data,
        pdf_file_text=text, 
        pdf_file_path=path, 
        tag=form.tag.data, 
        description=form.description.data,
        author_id=current_user.id,
        content=content
    )
    db.session.add(study)
    db.session.commit()

    return redirect(url_for('case_studies'))
    
@app.route('/case-study/<int:id>', methods=['GET', 'POST'])
def case_study(id):
    case_study = CaseStudy.query.get_or_404(id)
    all_comments = Comment.query.order_by(Comment.timestamp)
    comments = [comment for comment in all_comments if comment.post_id == id]
    comment_form = CommentCreationForm()
    return render_template('case-study.html', case_study=case_study, comments=comments, comment_form=comment_form, current_user=current_user)

@app.route('/case-study/<int:id>/delete')
def delete_case_study(id):
    case_study = CaseStudy.query.get_or_404(id)
    db.session.delete(case_study)
    db.session.commit()
    return redirect(url_for('case_studies'))


@app.route('/case-study/<int:id>/create-comment', methods=['POST'])
def create_comment(id):
    if not current_user.is_authenticated:
        flash('Veuillez vous connecter', 'error')
    user =  (current_user.id)

    form = CommentCreationForm()
    comment = Comment(content=form.content.data, author_id=user.id, post_id=id)
    db.session.add(comment)
    db.session.commit()

    return redirect(url_for(f'case_study', id=id))

@app.route('/case-study/<int:case_study_id>/delete-comment/<int:comment_id>')
def delete_comment(case_study_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('case_study', id=case_study_id))

@app.route('/case-study/<int:id>/take-quiz')
def take_quiz(id):
    if not current_user.is_authenticated:
        flash('Veuillez vous connecter', 'error')

    case_study = CaseStudy.query.get_or_404(id)

    return render_template('quiz.html', id=id, case_study=case_study)

@app.route('/case-study/<int:id>/take-quiz/questions')
def quiz_questions(id):
    if not current_user:
        flash('Veuillez vous connecter', 'error')

    study = db.session.scalar(sa.select(Project).where(Project.id == id))
    if study is None:
        return "Study not found f"

    return generate_quiz(study.case_study)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
