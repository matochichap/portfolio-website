from flask import Flask, render_template, url_for, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
import os

year = datetime.now().year
hashed_password = os.environ.get("PASSWORD")

app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db' local access to projects.db
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL_ALT", 'sqlite:///projects.db')  # heroku projects.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class ProjectForm(FlaskForm):
    title = StringField("Project Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Project Image URL", validators=[DataRequired(), URL()])
    github_url = StringField("Github URL", validators=[DataRequired(), URL()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class DeleteProjectForm(FlaskForm):
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class Projects(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(1000), nullable=False)
    github_url = db.Column(db.String(1000), nullable=False)


db.create_all()


@app.route('/')
def home():
    return render_template("index.html", year=year)


@app.route('/projects')
def projects():
    all_projects = Projects.query.all()
    return render_template("projects.html", year=year, projects=all_projects)


@app.route('/about')
def about():
    return render_template("about.html", year=year)


@app.route('/add', methods=["GET", "POST"])
def add():
    form = ProjectForm()
    if form.validate_on_submit():
        if check_password_hash(hashed_password, form.password.data):
            new_project = Projects(
                title=form.title.data,
                subtitle=form.subtitle.data,
                img_url=form.img_url.data,
                github_url=form.github_url.data
            )
            db.session.add(new_project)
            db.session.commit()
            return redirect(url_for("projects"))
        else:
            flash("Incorrect password!")
            return redirect(url_for("add"))

    return render_template("change_project.html", year=year, form=form, mode="add")


@app.route('/edit/<int:project_id>', methods=["GET", "POST"])
def edit(project_id):
    project = Projects.query.get(project_id)
    edit_form = ProjectForm(
        title=project.title,
        subtitle=project.subtitle,
        img_url=project.img_url,
        github_url=project.github_url
    )
    if edit_form.validate_on_submit():
        if check_password_hash(hashed_password, edit_form.password.data):
            project.title = edit_form.title.data
            project.subtitle = edit_form.subtitle.data
            project.img_url = edit_form.img_url.data
            project.github_url = edit_form.github_url.data
            db.session.commit()
            return redirect(url_for("projects"))
        else:
            flash("Incorrect password!")
            return redirect(url_for("edit", project_id=project_id))
    return render_template("change_project.html", year=year, form=edit_form, mode="edit")


@app.route('/delete/<int:project_id>', methods=["GET", "POST"])
def delete(project_id):
    project = Projects.query.get(project_id)
    delete_form = DeleteProjectForm()
    if delete_form.validate_on_submit():
        if check_password_hash(hashed_password, delete_form.password.data):
            db.session.delete(project)
            db.session.commit()
            return redirect(url_for("projects"))
        else:
            flash("Incorrect password!")
            return redirect(url_for("delete", project_id=project_id))
    return render_template("change_project.html", year=year, form=delete_form, mode="delete")


if __name__ == "__main__":
    app.run(debug=True)
