from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import User, Roster, Config
from django.db import connection
from django.db.models.expressions import RawSQL
import requests
import random
import string
from io import BytesIO
from captcha.image import ImageCaptcha

def generate_captcha_text(length=4):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def captcha_view(request):
    image = ImageCaptcha(width=160, height=60)
    captcha_text = generate_captcha_text()
    request.session['captcha'] = captcha_text
    print('new captcha:', captcha_text)
    data = image.generate(captcha_text)
    return HttpResponse(data.read(), content_type='image/png')

def login_view(request):
    """
    Handles user login with CAPTCHA verification, LDAP authentication,
    and fallback to local database authentication. Supports "Remember Me".
    """

    print("=== login_view called ===")

    # Step 0: Check if the user is already authenticated
    if request.user.is_authenticated:
        print(f"User already authenticated: {request.user.username}")
        return redirect('index')

    # Step 1: Only handle POST requests for login attempts
    if request.method == 'POST':
        print("POST request detected. Processing login form...")

        # Extract login form fields from POST data
        username = request.POST.get('username')
        password = request.POST.get('password')
        captcha_input = request.POST.get('captcha')
        remember = True if request.POST.get('remember') else False

        print(f"Form input -> Username: {username}, Remember: {remember}, Captcha: {captcha_input}")

        # Step 2: Validate CAPTCHA before any authentication
        stored_captcha = request.session.get('captcha')
        print(f"Stored CAPTCHA in session: {stored_captcha}")
        if captcha_input != stored_captcha:
            print("CAPTCHA mismatch!")
            messages.error(request, 'Incorrect CAPTCHA')
            return render(request, 'auth/login.html')

        # Step 3: Prepare LDAP/External API authentication parameters
        auth_url = settings.AUTH_API_URL
        auth_key = settings.AUTH_API_KEY
        verify_ssl = settings.AUTH_API_VERIFY_SSL
        print(f"LDAP API URL: {auth_url}, verify_ssl: {verify_ssl}")

        try:
            # Step 3a: Request an authentication token from LDAP API
            print("Requesting LDAP token...")
            token_response = requests.post(
                f"{auth_url}/request_token",
                json={'username': username, 'password': password},
                headers={'X-API-Key': auth_key},
                verify=verify_ssl,
                timeout=10
            )
            token_data = token_response.json()
            print(f"LDAP token response: {token_data}")

            if token_data.get('success'):
                token = token_data['token']
                print(f"Token received: {token}")

                # Step 3b: Fetch user information using the token
                print("Requesting user info from LDAP...")
                user_info_response = requests.post(
                    f"{auth_url}/user_info",
                    json={'token': token},
                    headers={'X-API-Key': auth_key},
                    verify=verify_ssl,
                    timeout=10
                )
                user_info_data = user_info_response.json()
                print(f"LDAP user info response: {user_info_data}")

                if user_info_data.get('success'):
                    api_user = user_info_data['user']
                    sAMAccountName = api_user['sAMAccountName']
                    print(f"LDAP user found: {sAMAccountName}")

                    # Step 3d: Sync LDAP user with local database
                    try:
                        user = User.objects.get(username=sAMAccountName)
                        print(f"User exists in local DB: {user.username}. Updating info...")
                        user.firstname = api_user.get('givenName')
                        user.lastname = api_user.get('sn')
                        user.set_password(password)
                        user.save()
                        print("Local user updated successfully.")
                    except User.DoesNotExist:
                        print("User not found in local DB. Creating new user...")
                        user = User.objects.create_user(
                            username=sAMAccountName,
                            password=password,
                            firstname=api_user.get('givenName'),
                            middlename=api_user.get('initials'),
                            lastname=api_user.get('sn'),
                            email=api_user.get('email'),
                            contact=api_user.get('mobile'),
                            group_id=8,
                            status='Active'
                        )
                        print(f"Local user created: {user.username}")

                    # Step 3e: Log the user in
                    login(request, user)
                    print(f"User logged in: {user.username}")
                    if not remember:
                        request.session.set_expiry(0)
                        print("Session set to expire on browser close.")

                    return redirect('index')

        except Exception as e:
            print(f"LDAP Auth Error: {str(e)}")
            messages.warning(request, 'LDAP authentication failed, trying local login.')

        # Step 4: Fallback to local database authentication
        print("Attempting local DB authentication...")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print(f"Local DB authentication successful. User logged in: {user.username}")
            if not remember:
                request.session.set_expiry(0)
                print("Session set to expire on browser close.")
            return redirect('index')

        # Step 5: Login failed
        print("Login failed: invalid username or password.")
        messages.error(request, 'Login failed. Please check your username and password.')

    # Step 6: Render login page for GET requests or failed logins
    print("Rendering login page...")
    return render(request, 'auth/login.html')
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def index(request):
    try:
        as_of_config = Config.objects.get(particular='ROSTER_DATE')
        data_as_of = as_of_config.value
    except Config.DoesNotExist:
        data_as_of = "N/A"

    return render(request, 'finder/index.html', {'data_as_of': data_as_of})

@login_required
def search_view(request):
    if request.method == 'POST':
        fname = request.POST.get('fname', '').strip()
        mname = request.POST.get('mname', '').strip()
        lname = request.POST.get('lname', '').strip()

        full_name_input = f"{fname} {mname} {lname}".strip()

        # Using raw SQL for similarity search
        with connection.cursor() as cursor:
            query = """
                SELECT *, similarity(CONCAT_WS(' ', first_name, middle_name, last_name), %s) AS similarity_score
                FROM ds.tbl_roster
                WHERE similarity(CONCAT_WS(' ', first_name, middle_name, last_name), %s) > 0.3
                ORDER BY similarity_score DESC
                LIMIT 20
            """
            cursor.execute(query, [full_name_input, full_name_input])

            # Fetch column names
            columns = [col[0] for col in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

        data = []
        for row in results:
            data.append({
                'hh_id': row['hh_id'],
                'name': f"{row['first_name']} {row['middle_name']} {row['last_name']}",
                'birthday': str(row['birthday']) if row['birthday'] else '',
                'address': f"BRGY. {row['barangay']}, {row['municipality']}",
                'client_status': row['client_status'],
                'similarity': f"{round(row['similarity_score'] * 100, 2)}%",
                'hh_set': row['hh_set'],
                'prog': row['prog']
            })

        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def roster_view(request):
    if request.method == 'POST':
        hh_id = request.POST.get('hh_id')
        if not hh_id:
            return JsonResponse({'success': False, 'message': 'HHID is required'})

        roster_members = Roster.objects.filter(hh_id=hh_id)

        data = []
        for member in roster_members:
            data.append({
                'entry_id': str(member.entry_id),
                'name': f"{member.first_name} {member.middle_name} {member.last_name}",
                'relation': member.relation_to_hh_head,
                'birthday': str(member.birthday) if member.birthday else '',
                'sex': member.sex,
                'status': member.member_status,
                'grantee': member.grantee
            })

        return JsonResponse({'success': True, 'roster': data})
    return JsonResponse({'error': 'Method not allowed'}, status=405)
