from weasyprint import HTML
from flask_login import current_user, login_required
from models import Resume
from flask import Response, render_template, redirect, url_for, request
from app import app, db


@app.route('/')
def home_page():
    return render_template('index.html', active_page='home')


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

        if not name or not email or not phone:
            error_message = "Please fill out all requried fields."
            return render_template('personal-data.html', error=error_message, active_page='personal_data')

        if not current_user.is_authenticated:
            error_message = "Please log in before create resume"
            return render_template('personal-data.html', error=error_message, active_page='personal_data')

        resume = Resume(name, email, phone, city, experience,
                        education, skills, user_id=current_user.id)

        try:
            db.session.add(resume)
            db.session.commit()
            app.logger.info("Resume added successfully")
        except Exception as e:
            app.logger.error(f"Error adding resume: {e}")
            db.session.rollback()

        return redirect(url_for('view_resume'))

    return render_template('personal-data.html', active_page='personal_data')


@app.route('/view-resume', methods=['GET'])
def view_resume():
    if not current_user.is_authenticated:
        error_message = "Please log in before create resume"
        return render_template('view-resume.html', error=error_message, active_page='view_resume')
    resume = Resume.query.filter_by(user_id=current_user.id).all()
    if not resume:
        return render_template('view-resume.html', resumes=resume, active_page='view_resume')

    return render_template('view-resume.html', resumes=resume, active_page='view_resume')


@app.route('/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_resume(id):
    resume = Resume.query.get(id)

    if not resume:
        app.logger.error("Resume not found")
        return redirect(url_for('view_resume'))

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
            app.logger.info("Resume update successfully!")
            return redirect(url_for('view_resume'))
        except Exception as e:
            db.session.rollback()  # откатываем изменения в случае ошибки
            app.logger.error(f"Erorr: changes on db worng {e}")

    return render_template("edit-resume.html", resume=resume, active_page='view_resume')


@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_resume(id):
    resume = Resume.query.filter_by(id=id).first()

    if not resume:
        app.logger.error("Resume not found")
        return redirect(url_for("view_resume"))

    if request.method == 'POST':
        try:
            db.session.delete(resume)
            db.session.commit()
            app.logger.info(f"Resume: {resume} successfully delete")
            return redirect(url_for('view_resume'))
        except Exception as e:
            app.logger.error(f"ERROR: change to db call except {e}")

    return render_template('view-resume.html', resume=resume)


@app.route("/generate-pdf/<int:id>")
@login_required
def generate_pdf(id):
    resume = Resume.query.filter_by(id=id).first()

    if not resume:
        app.logger.error("Resume nor found")
        return redirect(url_for("view_resume"))
    try:
        html_content = render_template('pdf.html', resume=resume)
        pdf = HTML(string=html_content).write_pdf()
        return Response(pdf, mimetype='application/pdf',
                        headers={"Content-Disposition": f"attachment; filename=resume_{id}.pdf"})
    except Exception as e:
        app.logger.error(f"Error generating PDF: {e}")
        return redirect(url_for("view_resume"))


@app.route("/view-resume/preview<int:id>")
@login_required
def preview_resume(id):
    resume = Resume.query.filter_by(id=id).first()
    return render_template('pdf.html', resume=resume)
