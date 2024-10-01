from app import app, db, login_manager
from models import User, Resume
from flask import render_template, request, redirect, url_for, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from weasyprint import HTML



@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if password != password2:
            return render_template('register.html', error=("Password not confirm. Return again, please."))
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return render_template('register.html', error=(f"User with username already exist!"))
            else:
                hashed_password = generate_password_hash(
                    password, method="pbkdf2:sha256")
                user = User(username=username, password=hashed_password)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('home_page'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # найти пользователя по имени
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home_page'))

        return render_template('login.html', error='Invalid username or password.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/fill-out-resume')
@login_required
def fill_out_resume():
    return redirect(url_for('personal_data'))


@app.route('/personal-data', methods=['GET', 'POST'])
def personal_data():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        city = request.form.get('city')
        experience = request.form.get('experience')
        education = request.form.get('education')
        skills = request.form.get('skills')

        resume = Resume(name, email, phone, city,
                        experience, education, skills, user_id=current_user.id)

        try:
            db.session.add(resume)
            db.session.commit()
            app.logger("Resume added successfully")
        except Exception as e:
            app.logger.error(f"Error adding resume: {e}")
            db.session.rollback()

        return redirect(url_for('view_resume'))

    return render_template('personal-data.html')


@app.route('/view-resume', methods=['GET', 'POST'])
@login_required  # гарантируем что пользователь залогинен
def view_resume():
    resume = Resume.query.filter_by(user_id=current_user.id).all()

    return render_template('view-resume.html', resumes=resume)


@app.route('/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_resume(id):

    resume = Resume.query.get(id)

    if request.method == 'POST':
        resume.name = request.form.get('name')
        resume.email = request.form.get('email')
        resume.phone = request.form.get('phone')
        resume.city = request.form.get('city')
        resume.experience = request.form.get('experience')
        resume.education = request.form.get('education')
        resume.skills = request.form.get('skills')

        try:
            db.session.commit()
            return redirect(url_for('view_resume'))
        except Exception as e:
            db.session.rollback()  # откатываем изменения в случае ошибки
            return f"Erorr: changes on db worng {e}"

    return render_template("edit-resume.html", resume=resume)


@app.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete_resume(id):
    resume = Resume.query.filter_by(id=id).first()

    if not resume:
        return "Resume not found", 404

    if request.method == 'POST':
        try:
            db.session.delete(resume)
            db.session.commit()
            app.logger.info(f"Resume: {resume} successfully delete")
            return redirect(url_for('view_resume'))
        except Exception as e:
            return f"ERROR: change to db call except {e}"

    return render_template('view-resume.html', resume=resume)


@app.route("/generate-pdf/<int:id>")
@login_required
def generate_pdf(id):
    try:
        resume = Resume.query.filter_by(id=id).first()
        html_content = render_template('pdf.html', resume=resume)

        pdf = HTML(string=html_content).write_pdf()
        return Response(pdf, mimetype='application/pdf',
                        headers={"Content-Disposition": f"attachment; filename=resume_{id}.pdf"})
    except Exception as e:
        return "Error: something happened with generate pdf", 404
