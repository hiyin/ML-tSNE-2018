"""
Views for user management.
"""
from pyramid.view import view_config
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.sql import select

from passlib.apps import custom_app_context as singleton_context
from passlib.hash import sha512_crypt

from .processing.gen_uid import gen_uid

import logging
log = logging.getLogger(__name__)

@view_config(route_name='login', renderer='login.html')
def login_view(request):
    if logged_in(request):
        return HTTPFound(location=request.route_url('dashboard'))

    login_url = request.route_url('login')
    # referrer = request.url
    # if referrer == login_url:
    #     referrer = '/'  # never use login form itself as came_from
    # came_from = request.POST.get('came_from', referrer)
    message = None
    email = None

    if request.POST:
        dbsess = request.dbsession
        email = request.POST['email'].strip()
        query = "SELECT * FROM registered_user WHERE email_address = :email"
        result = dbsess.execute(query, {'email':email})
        user = result.fetchone()
        log.info(user)
        if user:
            # user exists
            uid = user.id
            password = request.POST['password']
            query = "SELECT password_hash FROM password WHERE user_id = :uid"
            result = dbsess.execute(query, {'uid': uid})
            user_password = result.fetchone()['password_hash']
            if singleton_context.verify(password, user_password):
                # login successful
                request.session['user'] = user
                headers = remember(request, email)
                dashboard_url = request.route_url('dashboard')
                # return HTTPFound(location=came_from, headers=headers)
                return HTTPFound(location=dashboard_url, headers=headers)
        else:
            # login failed
            message = 'Incorrect login details'

    return dict(
        message=message,
        url=login_url,
        # came_from=came_from,
        email=email,
    )

@view_config(route_name='register',
             renderer='register.html')
def register_view(request):
    if logged_in(request):
        return HTTPFound(location=request.route_url('dashboard'))

    register_url = request.route_url('register')
    message = None

    if request.POST:
        log.info(request.POST)
        dbsess = request.dbsession
        #for new user - no validation as this should be done client side prior to successful form submission
        email_address = request.POST['email_address'].strip()

        # check user does not already exist
        query = "SELECT * FROM registered_user WHERE email_address = :email"
        result = dbsess.execute(query, {'email': email_address})
        if result.rowcount != 0:
            message = 'ERROR: user with that email address already exists.'
            return dict(message=message, url=register_url)

        # hash password
        password = request.POST['password']
        hashed_password = singleton_context.encrypt(password)

        # get remaining info from form
        first_name = request.POST['first_name']
        secret_question = request.POST['secret_question']
        secret_answer = request.POST['secret_answer']
        hashed_answer = singleton_context.encrypt(secret_answer)

        last_name = request.POST.get('last_name', '')
        sector_id = request.POST.get('sector_id', '')
        organisation = request.POST.get('organisation', '')
        gender = request.POST.get('gender', '')
        date_of_birth = request.POST.get('date_of_birth', '')
        sector_id = request.POST.get('sector_id', '')

        user_id = gen_uid()
        password_id = gen_uid()
        privilege_id = 1

        # prepare SQL statements
        user_insert = ("INSERT INTO registered_user(id, privilege_id, {} "
                    "first_name, email_address, secret_question, secret_answer, "
                    "last_name, organisation, gender, date_of_birth) "
                    "VALUES (:uid, :privid, {} :fname, :email, "
                    ":secq, :seca, :lname, :org, :gender, :dob);")
        # hack to get around fk constraint
        if sector_id:
            user_insert = user_insert.format("sector_id,", ":sectorid")
        else:
            user_insert = user_insert.format("", "")

        user_values = dict(uid=user_id, privid=privilege_id,
                        sectorid=sector_id, fname=first_name,
                        email=email_address,
                        secq=secret_question, seca=hashed_answer,
                        lname=last_name, org=organisation,
                        gender=gender, dob=date_of_birth)
        password_insert = ("INSERT INTO password(id, user_id, password_hash) "
                        "VALUE (:pwid, :uid, :pwd);")
        pword_values = dict(pwid=password_id, uid=user_id, pwd=hashed_password)
        try:
            dbsess.execute(user_insert, user_values)
            dbsess.execute(password_insert, pword_values)
            dbsess.commit()
            # now log them in
            query = "SELECT * FROM registered_user WHERE email_address = :email"
            result = dbsess.execute(query, {'email':email_address})
            user = result.fetchone()
            request.session['user'] = user
            headers = remember(request, email_address)
            return HTTPFound(location=request.route_url('new'), headers=headers)
        except Exception as e:
            log.info(str(e))
            dbsess.rollback()
            message = "ERROR: failed to create user."

    return dict(
        message=message,
        url=register_url,
    )

@view_config(route_name='forgot_password',
             renderer='forgot_password.html')
def forgot_password_view(request):
    return {}

@view_config(route_name='logout')
def logout_view(request):
    if logged_in(request):
        del request.session['user']
    return HTTPFound(location = request.application_url, headers = forget(request))

def logged_in(request):
    return 'user' in request.session
