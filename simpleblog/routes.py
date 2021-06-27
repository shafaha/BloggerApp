import secrets
import os
from PIL import Image
from simpleblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from flask import render_template, url_for, request, flash, redirect, abort
from simpleblog import app, bcrypt, db, mail
from simpleblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/", methods = ['POST', 'GET'])
@app.route("/home", methods = ['POST', 'GET'])
def home():
    page = request.args.get('page', 1, type = int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page = 2, page = page)
    return render_template('home.html', posts = posts)




def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    #resizing the image
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/register', methods = ['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect('home')

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        

        user = User(username = form.username.data,
                    email = form.email.data,
                    password = hashed_password)
        if form.picture.data :
            picture_path = save_picture(form.picture.data)
            user.picture = picture_path
        
        db.session.add(user)
        db.session.commit()
        flash(f'Accounts created for {form.username.data}', 'success')
        return redirect(url_for('login'))
    if form.username.data != None:
        flash(f'Accounts not created for {form.username.data}', 'danger')
    return render_template('register.html', title = 'Register', form = form)

@app.route('/login', methods= ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):  
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                print(next_page)
                return redirect(url_for('account'))
            else:
                return redirect(url_for('home'))
        else:
            flash("Login Unsuccessful, Please check email and password")
        
    return render_template('login.html', title = "Login", form = form)


@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))




@app.route("/account", methods = ['GET', 'POST'])
@login_required
def account():
    
    form = UpdateAccountForm()
    image_file = None
    if form.validate_on_submit():
        
        if form.picture.data:
            print("HEllo world")
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated", 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    if image_file == None:
        image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    print(image_file)
    return render_template('accounts.html', title = "User Info", image_file = image_file, form = form)



@app.route('/post/<int:post_id>', methods = ['GET', 'POST'] )
def post(post_id):
    posts = Post.query.get_or_404(post_id)
    return render_template('post.html', post = posts, title = posts.title)

@app.route("/post/new", methods = ['GET','POST'])
@login_required
def new_post():
    legend_value = "New Post"
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title = form.title.data,
            content = form.content.data,
            author = current_user
        )
        db.session.commit()
        flash("Your Post Has been created", 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title = 'New Post', form = form, Legend = legend_value)

@app.route("/post/<int:post_id>/update", methods = ['GET', 'POST'])
@login_required
def update_post(post_id):
    legend_value = "Update Post"
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    else:
        form = PostForm()
        if request.method == 'GET':
            form.content.data = post.content
            form.title.data = post.title
        else:
            if form.validate_on_submit():
                post.title= form.title.data
                post.content = form.content.data
                db.session.commit()
                flash('Your post has been updated', 'success')
                return redirect(url_for('post', post_id = post.id))        
    return render_template('create_post.html', form = form,  Legend = legend_value)

@app.route("/post/<int:post_id>/delete", methods = ['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post.author !=current_user:
        abort(403)
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Your post has been deleted", 'success')
        return redirect(url_for('home'))
    
        


@app.route("/user/<string:username>", methods = ['POST', 'GET'])
def user_posts(username):
    page = request.args.get('page', 1, type = int)
    user = User.query.filter_by(username = username).first_or_404()
    if user:
        posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc()).paginate(per_page = 2, page = page)
    return render_template('user_posts.html', posts = posts,  user =  user)


def send_reset_email(user):
    token = user.get_reset_token(18000)
    msg = Message('Password Reset request', sender = "noreply@demo.com", recipients = [user.email])

    msg.body = f'''
To reset the password visit the below link:

{url_for('reset_token', token = token, _external = True)}
'''
    mail.send(msg)


@app.route("/reset_password", methods = ['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit:
        user = User.query.filter_by(email=form.email.data).first()
        if user != None:
            send_reset_email(user)
            flash("An email has been sent with instructions to reset your password")
            return redirect(url_for('login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)


@app.route("/reset_password/<token>", methods = ["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)
    if user is None:
        flash("Invalid or expired token", 'warning')
        return redirect(url_for('reset_request'))
    form = ResetForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Password changed successfully for {form.username.data}', 'success')
        return redirect(url_for('login'))
    if form.username.data != None:
        flash(f'Accounts not created for {form.username.data}', 'danger')
    return render_template("reset_token.html", title = "Reset Password", form = form)


    

    

