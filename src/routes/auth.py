from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from src.models.user import User, db
# It's good practice to have a dedicated form class, but for simplicity, we'll handle form data directly for now.

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "master":
            return redirect(url_for("main.dashboard_master")) # Assuming a main blueprint with this route
        else:
            return redirect(url_for("main.dashboard_loja")) # Assuming a main blueprint with this route

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user) # remember=True can be added if a "remember me" checkbox is implemented
            flash("Login bem-sucedido!", "success")
            # Redirect based on role
            if user.role == "master":
                return redirect(url_for("main.dashboard_master"))
            elif user.role == "loja":
                return redirect(url_for("main.dashboard_loja"))
            else:
                return redirect(url_for("main.index")) # Fallback, should ideally not happen
        else:
            flash("Usuário ou senha inválidos. Tente novamente.", "danger")
            return redirect(url_for("auth.login"))
            
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("auth.login"))

# It might be useful to have a registration route for initial setup or if users can self-register in the future.
# For now, users will be created manually or via a script.

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))
