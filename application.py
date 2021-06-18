from flask import Flask, render_template, request, session, redirect, url_for, abort
from flask_bcrypt import Bcrypt
from models import *

from config import Config

thisConfig = Config()


app = Flask(__name__)
app.secret_key = thisConfig.SECRET_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = thisConfig.DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

bcrypt = Bcrypt(app)


@app.route('/')
def index():
	if 'login_user' not in session:
		login_user=None
	else:
		login_user=session['login_user']
	page = render_template('index.html', login_user=login_user)
	return page

@app.route('/about')
def about():
	return 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam faucibus egestas nunc, ut mattis tellus viverra eget. Sed malesuada ipsum eget ante suscipit consequat. Proin suscipit ligula sed lacinia volutpat. Donec nec nulla velit. Sed sed ligula eu nisi scelerisque gravida. Morbi scelerisque sem enim, id tincidunt leo fermentum vitae. Proin a mattis felis. Nulla eleifend dolor quis posuere facilisis. Maecenas gravida dui lacus, eget rhoncus libero suscipit ut. Nunc sed ullamcorper urna. Sed id nunc urna. Donec sit amet dolor orci. Aliquam erat volutpat. Proin sed risus facilisis turpis sollicitudin mollis sit amet ac metus. Maecenas eu lobortis nulla. Suspendisse id luctus risus.'

def validate_name(name):
	if len(name)<3:
		return False, "Empty First/Last Name Field or less then 3 characters.", "danger"
	return True, "created", "success"

def validate_username(username):
	if len(username)<5:
		return False, "Empty Username Field or less then 5 characters.", "danger"
	user = User.query.filter_by(username=username).first()
	#user = User.query.filter(User.username == username).first()
	if user:
		return False, "Username already exists.", "danger"
	return True, "created", "success"

def validate_password(password, confirm):
	if len(password)<5:
		return False, "Empty Password Field or less then 5 characters.", "danger"
	if password != confirm:
		return False, "Password doesn't match.", "danger"
	return True, "created", "success"

@app.route('/register', methods=['GET', 'POST'])
def register():
	if 'login_user' in session:
		return redirect(url_for('index'))
	if request.method == 'POST':
		f_name = request.form.get('first_name')
		l_name = request.form.get('last_name')
		username = request.form.get('username')
		password = request.form.get('password')
		confirm = request.form.get('confirm')

		validation_f_name = validate_name(f_name)
		if validation_f_name[0] == False:
			return render_template('register.html', msg=validation_f_name[1], category=validation_f_name[2])

		validation_l_name = validate_name(l_name)
		if validation_l_name[0] == False:
			return render_template('register.html', msg=validation_l_name[1], category=validation_l_name[2])

		validation_username = validate_username(username)
		if validation_username[0] == False:
			return render_template('register.html', msg=validation_username[1], category=validation_username[2])

		validation_password = validate_password(password, confirm)
		if validation_password[0] == False:
			return render_template('register.html', msg=validation_password[1], category=validation_password[2])

		hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
		user = User(first_name=f_name, last_name=l_name, username=username, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		return render_template('register.html', msg="Account Has Been Created", category="success")

	return render_template('register.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
	if 'login_user' not in session:
		return redirect(url_for('index'))

	login_user=session['login_user']

	notes = db.session.query(Note, User).filter(Note.created_by == User.id, Note.created_by == login_user['id']).order_by(Note.created_on.desc()).all()
	
	if request.method == 'POST':
		title = request.form.get('title')
		note = request.form.get('note')
		
		my_note = Note(created_by=login_user['id'], title=title, note=note)
		db.session.add(my_note)
		db.session.commit()
		return redirect(url_for('.create'))
	return render_template('create.html', login_user=login_user, notes=notes)

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit(note_id):
	if 'login_user' not in session:
		return redirect(url_for('index'))
	note = Note.query.get(note_id)
	login_user = session['login_user']
	if not note:
		abort(404) #Not Found
	if note.created_by != session['login_user']['id']:
		abort(403) #Permission Denied
	if request.method == 'POST':
		title_form = request.form.get('title')
		note_form = request.form.get('note')
		
		note.title = title_form
		note.note = note_form		
		db.session.commit()
		return redirect(url_for('.create'))

	return render_template('edit.html', note=note, login_user=login_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if 'login_user' in session:
		return redirect(url_for('.index'))
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		user = User.query.filter_by(username=username).first()
		if user:
			#if user.password == password :
			if bcrypt.check_password_hash(user.password, password):
				session['login_user'] = {
					'id' : user.id,
					'username' : user.username,
					'first_name' : user.first_name,
					'last_name' : user.last_name
				}
				return redirect(url_for('.index'))
		return render_template('login.html', msg="Login Failed", category="danger")
	return render_template('login.html')


@app.route('/logout')
def logout():
	if 'login_user' in session:
		session.pop('login_user')
	return redirect(url_for('.index'))

@app.route('/admin')
def admin():
	pass

@app.route('/api/user/<string:username>')
def user_api(username):
	return username


@app.route('/api/note/<int:note_id>')
def note_api(note_id):
	return note_id

@app.route('/delete/<int:note_id>', methods=['GET', 'POST'])
def delete(note_id):
	if 'login_user' not in session:
		return redirect(url_for('index'))
	# note = Note.query.get_or_404(note_id).first()
	note = Note.query.get(note_id)
	if not note :
		abort(404) #Not Found
	if note.created_by != session['login_user']['id']:
		abort(403) #Permission Denied

	db.session.delete(note)
	db.session.commit()

	return redirect(url_for('.create'))