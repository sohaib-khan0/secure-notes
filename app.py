from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate  # Import Migrate
from encryption import encrypt_message, decrypt_message
from forms import RegistrationForm, LoginForm, ResetPasswordForm, EditNoteForm, SearchForm
from models import db, User, Note

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'  # Replace with a secure key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash("Password reset successfully!", "success")
            return redirect(url_for("login"))
        else:
            flash("Username not found", "danger")
    return render_template("reset_password.html", form=form)

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    form = EditNoteForm()
    search_form = SearchForm()
    if form.validate_on_submit():
        encrypted_content = encrypt_message(form.content.data)
        note = Note(content=encrypted_content, user_id=current_user.id)
        db.session.add(note)
        db.session.commit()
        flash("Note saved!", "success")
        return redirect(url_for("dashboard"))

    user_notes = Note.query.filter_by(user_id=current_user.id).all()
    decrypted_notes = [(note.id, decrypt_message(note.content)) for note in user_notes]
    return render_template("dashboard.html", form=form, notes=decrypted_notes, search_form=search_form)

@app.route("/edit_note/<int:note_id>", methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for("dashboard"))
    form = EditNoteForm()
    if form.validate_on_submit():
        note.content = encrypt_message(form.content.data)
        db.session.commit()
        flash("Note updated!", "success")
        return redirect(url_for("dashboard"))
    form.content.data = decrypt_message(note.content)
    return render_template("edit_note.html", form=form)

@app.route("/delete_note/<int:note_id>")
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for("dashboard"))
    db.session.delete(note)
    db.session.commit()
    flash("Note deleted!", "success")
    return redirect(url_for("dashboard"))

@app.route("/search", methods=['GET', 'POST'])
@login_required
def search_notes():
    form = SearchForm()
    if request.method == 'POST' and form.validate_on_submit():
        query = form.query.data.lower()
        user_notes = Note.query.filter_by(user_id=current_user.id).all()
        results = [(note.id, decrypt_message(note.content)) for note in user_notes if query in decrypt_message(note.content).lower()]
        return render_template("search_results.html", notes=results, query=query)
    return render_template("search.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates the database tables if they don't exist
    app.run(host='0.0.0.0', port=5000, debug=True)  # Updated to listen on all interfaces
