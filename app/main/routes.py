from flask import render_template, redirect, url_for, flash, request, current_app
from app import db
from app.main import bp
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from flask_login import current_user, login_required
from app.models import User, Post
from datetime import datetime


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_access = datetime.utcnow()
        db.session.commit()


@bp.route('/')
@bp.route('/index/')
@login_required
def index():
    return render_template('index.html', title='Homepage')


@bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your Changes have been saved')
        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/blog', methods=['GET', 'POST'])
@login_required
def blog():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Post is now live!')
        return redirect(url_for('main.blog'))  # follows " POST/REDIRECT/GET " format

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('main.blog', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.blog', page=posts.prev_num) if posts.has_prev else None

    return render_template('blog.html', title='Blog Posts', posts=posts.items,
                           form=form, next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('blog.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    page = request.args.get('page', 1, type=int)
    posts = user.post.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('main.user_profile', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user_profile', username=user.username, page=posts.prev_num) if posts.has_prev else None

    return render_template('user.html', title='Profile', user=user, posts=posts,
                           form=form, next_url=next_url, prev_url=prev_url)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found!')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot follow yourself')
            return redirect(url_for('main.index'))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username} !')
        return redirect(url_for('main.user_profile', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found!')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.index'))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username} !')
        return redirect(url_for('main.user_profile', username=username))
    else:
        return redirect(url_for('main.index'))


