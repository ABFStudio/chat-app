from flask import Blueprint, redirect, url_for, request, flash
from flask_login import current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

import os
import json

from ..server import db
from ..utils import sm_parse_raw_image, sm_save_file
from .. import logger, UPLOAD_PREFIX

settings = Blueprint('settings', __name__, url_prefix='/settings')

@settings.route('/update/profile-picture', methods=['POST'])
def update_profile_picture():
    raw_image = json.loads(request.data.decode('utf-8'))
    img_data = sm_parse_raw_image(raw_image)
    image_name = secure_filename(img_data[0])
    img_content = img_data[1]
    sm_save_file(UPLOAD_PREFIX + 'pp/' + image_name, img_content)
    current_user.profile_picture = f'files/pp/{image_name}'
    db.session.commit()
    flash('Profile picture updated successfully!', category='success')
    return redirect(url_for('views.settings_page'))

@settings.route('/update/password', methods=['POST'])
def update_password():
    old_password = request.form.get('old-password')
    new_password = request.form.get('new-password')
    confirm_new_password = request.form.get('confirm-new-password')
    if check_password_hash(current_user.password, old_password):
        if len(new_password) < 10:
            flash('Your password must be at least 10 characters long!', category='error')
        elif new_password != confirm_new_password:
            flash('Passwords do not match!', category='error')
        else:
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully!', category='success')
    else:
        flash('Current password is incorrect!', category='error')
    return redirect(url_for('views.password'))