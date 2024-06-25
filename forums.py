from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, Forum, Comment, Reply
from forms import CommentForm, ReplyForm, ForumForm
from datetime import datetime
from werkzeug.utils import secure_filename
import os

forums = Blueprint('forums', __name__)

@forums.route('/')
def list_forums():
    all_forums = Forum.query.all()
    return render_template('forum.html', forums=all_forums)

@forums.route('/<int:forum_id>')
def forum_details(forum_id):
    forum = Forum.query.get_or_404(forum_id)
    forum.views_count += 1
    db.session.commit()
    return render_template('forum_details.html', forum=forum)

@forums.route('/add', methods=['GET', 'POST'])
def add_forum():
    form = ForumForm()
    if form.validate_on_submit():
        title = form.title.data
        # image_url = form.image_url.data
        text = form.text.data
        user_id = session.get('user_id')

        new_forum = Forum(title=title, text=text, user_id=user_id)
        db.session.add(new_forum)
        db.session.commit()
        
        flash('Forum added successfully!', 'success')
        return redirect(url_for('forums.list_forums'))
    
    return render_template('add_forum.html', form=form)


@forums.route('/<int:forum_id>/add_comment', methods=['GET', 'POST'])
def add_comment(forum_id):
    forum = Forum.query.get_or_404(forum_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        text = form.text.data
        pdf_file = form.pdf_file.data
        
        # Handle file upload if provided
        if pdf_file:
            filename = secure_filename(pdf_file.filename)
            pdf_path = os.path.join('uploads', filename)
            pdf_file.save(pdf_path)
            # You can save `pdf_path` to your database if needed
        
        # Get user ID from session (replace `1` with your actual session key)
        user_id = session.get('user_id')
        
        # Create new comment
        new_comment = Comment(text=text, user_id=user_id, forum_id=forum.id, date_added=datetime.utcnow())
        db.session.add(new_comment)
        db.session.commit()
        
        flash('Comment added successfully!', 'success')
        return redirect(url_for('forums.forum_details', forum_id=forum.id))
    
    return render_template('add_comment.html', form=form, forum=forum)
# Route to add a reply to a comment

@forums.route('/<int:forum_id>/<int:comment_id>/add_reply', methods=['GET', 'POST'])
def add_reply(forum_id, comment_id):
    forum = Forum.query.get_or_404(forum_id)
    comment = Comment.query.get_or_404(comment_id)
    form = ReplyForm()
    
    if form.validate_on_submit():
        text = form.text.data
        
        # Create new reply with current user's ID
        new_reply = Reply(text=text, user_id= session.get('user_id'), comment_id=comment.id, date_added=datetime.utcnow())
        db.session.add(new_reply)
        db.session.commit()
        
        flash('Reply added successfully!', 'success')
        return redirect(url_for('forums.forum_details', forum_id=forum.id))
    
    return render_template('add_reply.html', form=form, forum=forum, comment=comment)

# Route to serve uploaded PDF files
@forums.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)