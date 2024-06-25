from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.file import FileField, FileAllowed

class ForumForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    # image_url = StringField('Image URL', validators=[URL()])
    text = TextAreaField('Text', validators=[DataRequired()])
    submit = SubmitField('Add Forum')



class CommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[DataRequired()])
    pdf_file = FileField('Upload PDF File', validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Submit')

class ReplyForm(FlaskForm):
    text = TextAreaField('Reply', validators=[DataRequired()])
    submit = SubmitField('Reply')

class CaseStudyCreationForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    tag = StringField('Sujet', validators=[DataRequired()])
    pdf_file = FileField('Fichier PDF', validators=[DataRequired()])
    submit = SubmitField('Enregistrer')


class CommentCreationForm(FlaskForm):
    content = TextAreaField('Ajouter un commentaire', validators=[DataRequired()])
    submit = SubmitField('Enregistrer')