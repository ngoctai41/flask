from flask import Flask, redirect, url_for, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret123'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MODELS
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    books = db.relationship('Book', backref='category')

# LOGIN MANAGER
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ADMIN VIEWS
class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class ReadOnlyView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False

    def is_accessible(self):
        return current_user.is_authenticated

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

admin = Admin(app, name='Trang Quản Trị', template_mode='bootstrap4', index_view=MyAdminIndexView())
admin.add_view(MyModelView(Book, db.session))
admin.add_view(MyModelView(Category, db.session))
admin.add_view(ReadOnlyView(User, db.session))

# ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect('/admin')
        else:
            flash("Sai tài khoản hoặc mật khẩu", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password='admin'))
            db.session.commit()
    app.run(debug=True)
