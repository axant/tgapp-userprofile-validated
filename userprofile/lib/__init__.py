# -*- coding: utf-8 -*-
from formencode import validators
from hashlib import md5
import tg
from tg import url
from tgext.pluggable import app_model, plug_url
from tg.i18n import ugettext as _, lazy_ugettext as l_


def get_profile_css(config):
    return url(config['_pluggable_userprofile_config'].get('custom_css',
        '/_pluggable/userprofile/css/style.css'))


def _get_user_gravatar(email_address):
    if not isinstance(email_address, bytes):
        email_address = email_address.encode('utf-8')
    mhash = md5(email_address).hexdigest()
    return url('http://www.gravatar.com/avatar/'+mhash, params=dict(s=32))


def get_user_data(user):
    user_data = getattr(user, 'profile_data', {'display_name': (l_('Display Name'), user.display_name),
                                               'email_address': (l_('Email Address'), user.email_address)})

    user_avatar = user_data.pop('avatar', None)
    if user_avatar is None:
        fbauth_info = getattr(user, 'fbauth', None)
        if fbauth_info is not None:
            user_avatar = fbauth_info.profile_picture + '?type=large'
        else:
            user_avatar = _get_user_gravatar(user_data['email_address'][1])

    return user_data, user_avatar

def update_user_data(user, user_data):
    for k, v in user_data.items():
        setattr(user, k, v)

if tg.config.get('prefer_toscawidgets2', False):
    from tw2.forms import ListForm, TextField, TextArea, HiddenField, FileField, SubmitButton, PasswordField
else:
    from tw.forms import ListForm, TextField, PasswordField

from formencode.validators import UnicodeString, FieldStorageUploadConverter
from sprox.formbase import FilteringSchema
from formencode.validators import FieldsMatch

_password_match = FieldsMatch('password', 'verify_password',
                              messages={'invalidNoMatch': l_('Passwords do not match')})

if hasattr(TextField, 'req'):
    change_password_form_validator = _password_match
else:
    change_password_form_validator =  FilteringSchema(chained_validators=[_password_match])

if tg.config.get('prefer_toscawidgets2', False):
    from tw2.core import Required

    class UserForm(ListForm):
        uid=HiddenField()
        submit=SubmitButton(value=l_('Save'))

    def create_user_form(user):
        profile_form = getattr(user, 'profile_form', None)
        if not profile_form:
            user_data, user_avatar = get_user_data(user)
            profile_form = UserForm()

            for name, info in user_data.items():
                profile_form.child = profile_form.child()
                profile_form.child.children.append(TextField(id=name, validator=Required, label=info[0]))

            profile_form = profile_form()
        return profile_form

    class ChangePasswordForm(ListForm):
        password = PasswordField(label=u'Password', validator=Required)
        verify_password = PasswordField(label=l_(u'Confirm Password'), validator=Required)
        submit=SubmitButton(value=l_('Save'))
        validator = change_password_form_validator

    def create_change_password_form():
        return ChangePasswordForm()
else:
    def create_user_form(user):
        profile_form = getattr(user, 'profile_form', None)
        if not profile_form:
            user_data, user_avatar = get_user_data(user)
            form_fields = [TextField(id=name, validator=UnicodeString(not_empty=True),
                                     label_text=info[0]) for name, info in user_data.items()]
            profile_form = ListForm(fields=form_fields, submit_text=l_('Save'),
                                    action=plug_url('userprofile', '/save'))
        return profile_form

    def create_change_password_form():
        return ListForm(fields=[PasswordField('password', label_text='Password',
                                              validator=UnicodeString(not_empty=True)),
                                PasswordField('verify_password', label_text=l_('Confirm Password'),
                                              validator=UnicodeString(not_empty=True))],
                        action=plug_url('userprofile', '/save_password', lazy=True),
                        validator=change_password_form_validator,
                        submit_text=l_('Save'))