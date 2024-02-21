import bcrypt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from .models import *


def index(request):
    """
    Отображение главной страницы.

    Проверяет, авторизован ли пользователь, иначе перенаправляет на страницу входа.

    :param request: Объект запроса Django.
    :return: Ответ с главной страницей или перенаправление на страницу входа.
    """
    try:
        login = request.COOKIES.get('user_login')

        role = Role.objects.get(login=login)
    except:
        return redirect('login')

    context = {
        'role': role.name
    }

    return render(request, 'mag/index.html', context=context)


def login(request):
    """
    Страница входа пользователя.

    Проверяет логин и пароль, устанавливает куки и перенаправляет на главную, или выводит ошибку.

    :param request: Объект запроса Django.
    :return: Ответ с страницей входа, главной или сообщением об ошибке.
    """
    error = ''

    context = {
        'error': error
    }

    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')

        try:
            role = Role.objects.get(login=login)

            if role.password == password:
                response = redirect('index')
                response.set_cookie('user_login', login)
                return response

            error = 'Неверный пароль'

            context = {
                'error': error
            }

            return render(request, 'mag/login.html', context)
        except Role.DoesNotExist:
            error = 'Такого пользователя не существует'

            context = {
                'error': error
            }

            return render(request, 'mag/login.html', context)

    return render(request, 'mag/login.html', context)


def signup(request):
    """
    Страница регистрации пользователя.

    Проверяет логин, пароль и другие условия, создает пользователя и перенаправляет на главную.

    :param request: Объект запроса Django.
    :return: Ответ с страницей регистрации, главной или сообщением об ошибке.
    """
    error = ''

    context = {
        'error': error
    }

    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')

        if not login or not password:
            error = 'Заполните все поля'

            context = {
                'error': error
            }

            return render(request, 'mag/signup.html', context)

        if len(password) < 8:
            error = 'Пароль должен содержать не менее 8 символов'

            context = {
                'error': error
            }

            return render(request, 'mag/signup.html', context)

        alphanumeric_validator = RegexValidator(r'^[0-9a-zA-Z]*$', 'Логин должен содержать только буквы и цифры')

        try:
            alphanumeric_validator(login)
        except ValidationError as e:
            error = e.message
            return render(request, 'mag/signup.html', {'error': error})

        roles = Role.objects.all()

        for r in roles:
            if r.login == login:
                error = 'Такой логин уже существует'

                context = {
                    'error': error
                }

                return render(request, 'mag/signup.html', context)

        role = Role(login=login, password=password, name='patient')
        role.save()

        response = redirect('index')
        response.set_cookie('user_login', login)
        return response

    return render(request, 'mag/signup.html', context)


def reception(request):
    """
    Страница записи на прием к врачу.

    Проверяет авторизацию, роль пользователя и производит запись на прием.

    :param request: Объект запроса Django.
    :return: Ответ с страницей записи на прием, главной или сообщением об ошибке.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')

    user = Role.objects.get(login=request.COOKIES.get('user_login'))

    if user.name != 'patient':
        return redirect('index')

    doctors = Doctor.objects.all()
    calendar = Calendar.objects.all()

    context = {
        'doctors': doctors,
        'calendar': calendar,
        'error': ''
    }

    try:
        patient = Patient.objects.get(role=user)
    except:
        context['error'] = 'Врач должен вас зарегистрировать как пациента'

        return render(request, 'mag/reception.html', context)

    if request.method == 'POST':
        direction = request.POST.get('specialty')
        doctor_id = request.POST.get('doctor')
        calendar_id = request.POST.get('schedule')

        doctor = Doctor.objects.get(id=doctor_id)
        calendar = Calendar.objects.get(id=calendar_id)

        if doctor == '0' or calendar == '0':
            context['error'] = 'Заполните все поля'

            return render(request, 'mag/reception.html', context)

        if direction and doctor and calendar:
            if calendar.doctor_id != doctor.id:
                context['error'] = 'Неверный доктор'

                return render(request, 'mag/reception.html', context)

            if direction != doctor.direction:
                context['error'] = 'Неверная специальность'

                return render(request, 'mag/reception.html', context)

            patient = Patient.objects.get(role=user)

            record = Record(calendar=calendar, recipe=None, patient=patient)
            record.save()

            return redirect('index')

        context['error'] = 'Заполните все поля'

        return render(request, 'mag/reception.html', context)

    return render(request, 'mag/reception.html', context=context)


def users(request):
    """
    Страница управления пользователями.

    Показывает список пациентов и врачей для администратора или медсестры.

    :param request: Объект запроса Django.
    :return: Ответ с страницей управления пользователями, главной или перенаправление на страницу входа.
    """
    users = Patient.objects.all()
    doctors = Doctor.objects.all()

    if not request.COOKIES.get('user_login'):
        return redirect('login')

    user = Role.objects.get(login=request.COOKIES.get('user_login'))

    if user.name != 'admin' and user.name != 'doctor':
        return redirect('index')

    roles = Role.objects.filter(name__in=['admin', 'nurse'])

    context = {
        'users': users,
        'doctors': doctors,
        'roles': roles
    }

    return render(request, 'mag/users.html', context)


# def notifications(request):
#
#     if not request.COOKIES.get('user_login'):
#         return redirect('login')
#
#     user = Role.objects.get(login=request.COOKIES.get('user_login'))
#
#     if user.name != 'patient':
#         return redirect('index')
#
#     return render(request, 'mag/notification.html')


def medical_card(request):
    """
    Страница медицинской карты пациента.

    Проверяет авторизацию и роль пользователя перед отображением страницы.

    :param request: Объект запроса Django.
    :return: Ответ с страницей медицинской карты, главной или перенаправление на страницу входа.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')

    user = Role.objects.get(login=request.COOKIES.get('user_login'))

    if user.name != 'patient':
        return redirect('index')

    try:
        patient = Patient.objects.get(role=user)
        medical_card = ElectronicCard.objects.get(patient=patient)

        context = {
            'medical_card': medical_card
        }
    except:
        context = {}

    return render(request, 'mag/medical_card.html', context)


def logout(request):
    """
    Выход пользователя из системы.

    Удаляет куки пользователя и перенаправляет на страницу входа.

    :param request: Объект запроса Django.
    :return: Перенаправление на страницу входа.
    """
    response = redirect('login')
    response.delete_cookie('user_login')
    return response


def delete_patient(request, id):
    """
    Удаление пациента.

    Проверяет авторизацию, роль пользователя и производит удаление пациента и связанной с ним роли.

    :param request: Объект запроса Django.
    :param id: Идентификатор пациента.
    :return: Перенаправление на страницу управления пользователями.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')

    user = Role.objects.get(login=request.COOKIES.get('user_login'))

    if user.name != 'admin' and user.name != 'doctor':
        return redirect('index')

    patient = Patient.objects.get(id=id)
    role = patient.role
    patient.delete()
    role.delete()

    return redirect('users')


def delete_doctor(request, id):
    """
    Удаление врача.

    Проверяет авторизацию, роль пользователя и производит удаление врача и связанной с ним роли.

    :param request: Объект запроса Django.
    :param id: Идентификатор врача.
    :return: Перенаправление на страницу управления пользователями.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')

    user = Role.objects.get(login=request.COOKIES.get('user_login'))

    if user.name != 'admin' and user.name != 'doctor':
        return redirect('index')

    doctor = Doctor.objects.get(id=id)
    role = doctor.role
    doctor.delete()
    role.delete()

    return redirect('users')


def delete_nurse(request, id):
    """
    Удаление медсестры.

    Проверяет авторизацию, роль пользователя и производит удаление медсестры.

    :param request: Объект запроса Django.
    :param id: Идентификатор медсестры.
    :return: Перенаправление на страницу управления пользователями.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')

    user = Role.objects.get(login=request.COOKIES.get('user_login'))

    if user.name != 'admin' and user.name != 'doctor':
        return redirect('index')

    nurse = Role.objects.get(id=id)
    nurse.delete()

    return redirect('users')


def edit_doctor(request, id):
    """
    Редактирование данных врача.

    Проверяет авторизацию, роль пользователя и производит редактирование данных врача.

    :param request: Объект запроса Django.
    :param id: Идентификатор врача.
    :return: Перенаправление на страницу управления пользователями или отображение формы редактирования.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'admin' and user.name != 'doctor':
            return redirect('index')

    doctor = Doctor.objects.get(id=id)
    roles = Role.objects.filter(name='doctor')

    context = {
        'doctor': doctor,
        'roles': roles,
        'error': ''
    }

    if request.method == 'POST':
        surname = request.POST.get('surname')
        name = request.POST.get('name')
        lastname = request.POST.get('lastname')
        direction = request.POST.get('direction')
        role = request.POST.get('role')

        if role == '0':
            context['error'] = 'Выберите роль'

            return render(request, 'mag/edit_doctor.html', context)

        if not surname or not name or not lastname or not direction:
            context['error'] = 'Заполните все поля'

            return render(request, 'mag/edit_doctor.html', context)

        role = Role.objects.get(id=role)

        doctor = Doctor.objects.get(id=id)
        doctor.surname = surname
        doctor.name = name
        doctor.lastname = lastname
        doctor.direction = direction
        doctor.role = role
        doctor.save()

        return redirect('users')

    return render(request, 'mag/edit_doctor.html', context=context)


def edit_patient(request, id):
    """
    Редактирование данных пациента.

    Проверяет авторизацию, роль пользователя и производит редактирование данных пациента.

    :param request: Объект запроса Django.
    :param id: Идентификатор пациента.
    :return: Перенаправление на страницу управления пользователями или отображение формы редактирования.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'admin' and user.name != 'doctor':
            return redirect('index')

    patient = Patient.objects.get(id=id)
    roles = Role.objects.filter(name='patient')
    cards = ElectronicCard.objects.all()

    context = {
        'patient': patient,
        'roles': roles,
        'cards': cards,
        'error': ''
    }

    if request.method == 'POST':
        surname = request.POST.get('surname')
        name = request.POST.get('name')
        lastname = request.POST.get('lastname')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        card = request.POST.get('electronic_card')
        role = request.POST.get('role')

        if role == '0':
            context['error'] = 'Выберите роль'

            return render(request, 'mag/edit_patient.html', context)

        if card != '0':
            card = ElectronicCard.objects.get(id=card)
        else:
            context['error'] = 'Выберите карту'
            return render(request, 'mag/edit_patient.html', context)

        if not surname or not name or not lastname or not phone_number or not email:
            context['error'] = 'Заполните все поля'

            return render(request, 'mag/edit_patient.html', context)

        role = Role.objects.get(id=role)

        patient = Patient.objects.get(id=id)
        patient.surname = surname
        patient.name = name
        patient.lastname = lastname
        patient.phone_number = phone_number
        patient.email = email
        card = ElectronicCard.objects.get(id=card)
        patient.electronic_card = card
        patient.role = role
        patient.save()

        return redirect('users')

    return render(request, 'mag/edit_patient.html', context=context)


def edit_another_user(request, id):
    """
    Редактирование данных другого пользователя.

    Проверяет авторизацию, роль пользователя и производит редактирование данных другого пользователя.

    :param request: Объект запроса Django.
    :param id: Идентификатор пользователя.
    :return: Перенаправление на страницу управления пользователями или отображение формы редактирования.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'admin' and user.name != 'doctor':
            return redirect('index')

    user = Role.objects.get(id=id)

    context = {
        'user': user,
        'error': ''
    }

    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if role == '0':
            context['error'] = 'Выберите роль'

            return render(request, 'mag/edit.html', context)

        if not login or not password:
            context['error'] = 'Заполните все поля'

            return render(request, 'mag/edit.html', context)

        alphanumeric_validator = RegexValidator(r'^[0-9a-zA-Z]*$', 'Логин должен содержать только буквы и цифры')

        try:
            alphanumeric_validator(login)
        except ValidationError as e:
            error = e.message
            return render(request, 'mag/signup.html', {'error': error})

        user = Role.objects.get(id=id)
        user.login = login
        user.password = password
        user.name = role
        user.save()

        return redirect('users')

    return render(request, 'mag/edit.html', context=context)


def add_patient(request):
    """
    Добавление нового пациента.

    Проверяет авторизацию, роль пользователя и производит добавление нового пациента.

    :param request: Объект запроса Django.
    :return: Перенаправление на страницу управления пользователями или отображение формы добавления пациента.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'admin' and user.name != 'doctor':
            return redirect('index')

    cards = ElectronicCard.objects.all()
    roles = Role.objects.filter(name='patient')

    context = {
        'cards': cards,
        'roles': roles,
        'error': ''
    }

    if request.method == 'POST':
        surname = request.POST.get('surname')
        name = request.POST.get('name')
        lastname = request.POST.get('lastname')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        card = request.POST.get('electronic_card')
        role = request.POST.get('role')

        if role == '0':
            context['error'] = 'Выберите роль'

            return render(request, 'mag/add_patient.html', context)

        if card == '0':
            context['error'] = 'Выберите карту'

            return render(request, 'mag/add_patient.html', context)

        if not surname or not name or not lastname or not phone_number or not email:
            context['error'] = 'Заполните все поля'

            return render(request, 'mag/add_patient.html', context)

        role = Role.objects.get(id=role)

        patient = Patient()
        patient.surname = surname
        patient.name = name
        patient.lastname = lastname
        patient.phone_number = phone_number
        patient.email = email
        card = ElectronicCard.objects.get(id=card)
        patient.electronic_card = card
        patient.role = role

        patient.save()

        return redirect('users')

    return render(request, 'mag/add_patient.html', context=context)


def add_doctor(request):
    """
    Добавление нового доктора.

    Проверяет авторизацию, роль пользователя и производит добавление нового доктора.

    :param request: Объект запроса Django.
    :return: Перенаправление на страницу управления пользователями или отображение формы добавления доктора.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'admin' and user.name != 'doctor':
            return redirect('index')

    roles = Role.objects.filter(name='doctor')

    context = {
        'roles': roles,
        'error': ''
    }

    if request.method == 'POST':
        surname = request.POST.get('surname')
        name = request.POST.get('name')
        lastname = request.POST.get('lastname')
        direction = request.POST.get('direction')
        role = request.POST.get('role')

        if role == '0':
            context['error'] = 'Выберите роль'

            return render(request, 'mag/add_doctor.html', context)

        if not surname or not name or not lastname or not direction:
            context['error'] = 'Заполните все поля'

            return render(request, 'mag/add_doctor.html', context)

        role = Role.objects.get(id=role)

        doctor = Doctor()
        doctor.surname = surname
        doctor.name = name
        doctor.lastname = lastname
        doctor.direction = direction
        doctor.role = role

        doctor.save()

        return redirect('users')

    return render(request, 'mag/add_doctor.html', context=context)


def add_another_user(request):
    """
    Добавление нового пользователя.

    Проверяет авторизацию, роль пользователя и производит добавление нового пользователя.

    :param request: Объект запроса Django.
    :return: Перенаправление на страницу управления пользователями или отображение формы добавления пользователя.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'admin' and user.name != 'doctor':
            return redirect('index')

        context = {
            'error': ''
        }

    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if role == '0':
            context['error'] = 'Выберите роль'

            return render(request, 'mag/add_role.html', context)

        if not login or not password:
            context['error'] = 'Заполните все поля'

            return render(request, 'mag/add_role.html', context)

        if Role.objects.filter(login=login).exists():
            context['error'] = 'Пользователь с таким логином уже существует'

            return render(request, 'mag/add_role.html', context)

        alphanumeric_validator = RegexValidator(r'^[0-9a-zA-Z]*$', 'Логин должен содержать только буквы и цифры')

        try:
            alphanumeric_validator(login)
        except ValidationError as e:
            error = e.message
            return render(request, 'mag/signup.html', {'error': error})

        user = Role()

        user.login = login
        user.password = password
        user.name = role

        user.save()

        return redirect('users')

    return render(request, 'mag/add_role.html', context)


def access_log(request):
    """
    Просмотр журнала доступа.

    Проверяет авторизацию и роль пользователя для просмотра журнала доступа.

    :param request: Объект запроса Django.
    :return: Перенаправление на страницу управления пользователями или отображение журнала доступа.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'admin' and user.name != 'doctor':
            return redirect('index')

    return render(request, 'mag/access_log.html')


def calendar(request):
    """
    Просмотр календаря.

    Проверяет авторизацию и роль пользователя для просмотра календаря.

    :param request: Объект запроса Django.
    :return: Перенаправление на страницу управления пользователями или отображение календаря.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'admin' and user.name != 'doctor' and user.name != 'nurse':
            return redirect('index')

    calendars = Calendar.objects.all()

    context = {
        'calendars': calendars
    }

    return render(request, 'mag/calendar.html', context)


def delete_calendar(request, id):
    """
    Удаление записи в календаре.

    Проверяет авторизацию, роль пользователя и удаляет запись в календаре.

    :param request: Объект запроса Django.
    :param id: Идентификатор записи в календаре для удаления.
    :return: Перенаправление на страницу календаря.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'admin' and user.name != 'doctor' and user.name != 'nurse':
            return redirect('index')

    calendar = Calendar.objects.get(id=id)
    calendar.delete()

    return redirect('calendar')


def edit_calendar(request, id):
    """
    Редактирование записи в календаре.

    Проверяет авторизацию, роль пользователя и производит редактирование записи в календаре.

    :param request: Объект запроса Django.
    :param id: Идентификатор записи в календаре для редактирования.
    :return: Перенаправление на страницу календаря или отображение формы редактирования записи.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'admin' and user.name != 'doctor' and user.name != 'nurse':
            return redirect('index')

    calendar = Calendar.objects.get(id=id)
    doctors = Doctor.objects.all()

    context = {
        'calendar': calendar,
        'doctors': doctors,
        'error': ''
    }

    if request.method == 'POST':
        schedule = request.POST.get('schedule')
        doctor = request.POST.get('doctor')

        if doctor == '0':
            context['error'] = 'Выберите врача'

            return render(request, 'mag/edit_calendar.html', context)

        if not schedule:
            context['error'] = 'Выберите время'

            return render(request, 'mag/edit_calendar.html', context)

        doctor = Doctor.objects.get(id=doctor)

        calendar = Calendar.objects.get(id=id)
        calendar.schedule = schedule
        calendar.doctor = doctor

        calendar.save()

        return redirect('calendar')

    return render(request, 'mag/edit_calendar.html', context)


def add_calendar(request):
    """
    Добавление записи в календарь.

    Проверяет авторизацию, роль пользователя и производит добавление записи в календарь.

    :param request: Объект запроса Django.
    :return: Перенаправление на страницу календаря или отображение формы добавления записи.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'admin' and user.name != 'doctor' and user.name != 'nurse':
            return redirect('index')

    doctors = Doctor.objects.all()

    context = {
        'doctors': doctors,
        'error': ''
    }

    if request.method == 'POST':
        schedule = request.POST.get('schedule')
        doctor = request.POST.get('doctor')

        if doctor == '0':
            context['error'] = 'Выберите врача'

            return render(request, 'mag/add_calendar.html', context)

        if not schedule:
            context['error'] = 'Выберите время'

            return render(request, 'mag/add_calendar.html', context)

        doctor = Doctor.objects.get(id=doctor)

        calendar = Calendar()
        calendar.schedule = schedule
        calendar.doctor = doctor

        calendar.save()

        return redirect('calendar')

    return render(request, 'mag/add_calendar.html', context)


def reception_nurse(request):
    """
    Прием пациентов медсестрой.

    Проверяет авторизацию и роль пользователя для отображения страницы приема пациентов медсестрой.

    :param request: Объект запроса Django.
    :return: Перенаправление на страницу входа или отображение страницы приема пациентов медсестрой.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')

    user = Role.objects.get(login=request.COOKIES.get('user_login'))

    if user.name != 'nurse':
        return redirect('index')

    if request.method == 'POST':
        direction = request.POST.get('specialty')
        doctor_id = request.POST.get('doctor')
        calendar_id = request.POST.get('schedule')
        patient = request.POST.get('patient')

        doctor = Doctor.objects.get(id=doctor_id)
        calendar = Calendar.objects.get(id=calendar_id)
        patient = Patient.objects.get(id=patient)

        if direction and doctor != '0' and calendar != '0' and patient != '0':
            if calendar.doctor_id != doctor.id:
                return render(request, 'mag/reception.html')

            if direction != doctor.direction:
                return render(request, 'mag/reception.html')

            record = Record(calendar=calendar, recipe=None, patient=patient)
            record.save()

            return redirect('index')


    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    calendar = Calendar.objects.all()

    context = {
        'doctors': doctors,
        'patients': patients,
        'calendar': calendar
    }

    return render(request, 'mag/reception_nurse.html', context)


def medical_card_nurse(request):
    """
    Просмотр медицинских карт медсестрой.

    Проверяет авторизацию и роль пользователя для отображения страницы просмотра медицинских карт медсестрой.

    :param request: Объект запроса Django.
    :return: Перенаправление на страницу входа или отображение страницы просмотра медицинских карт медсестрой.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')

    user = Role.objects.get(login=request.COOKIES.get('user_login'))

    if user.name != 'nurse':
        return redirect('index')

    patients = Patient.objects.all()

    context = {
        'patients': patients
    }

    return render(request, 'mag/medical_card_nurse.html', context)


def edit_mediacal_card(request, id):
    """
    Редактирование медицинской карты медсестрой.

    Проверяет авторизацию и роль пользователя для отображения страницы редактирования медицинской карты медсестрой.

    :param request: Объект запроса Django.
    :param id: Идентификатор медицинской карты для редактирования.
    :return: Перенаправление на страницу входа или отображение страницы редактирования медицинской карты медсестрой.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'nurse':
            return redirect('index')

    electronic_card = ElectronicCard.objects.get(id=id)
    patients = Patient.objects.all()

    context = {
        'card': electronic_card,
        'patients': patients,
        'error': ''
    }

    if request.method == 'POST':
        medical_card = request.POST.get('medical_card')
        result = request.POST.get('result')
        diagnosis = request.POST.get('diagnosis')
        treatment = request.POST.get('treatment')
        patient_id = request.POST.get('patient')

        electronic_card = ElectronicCard.objects.get(id=id)

        if patient_id == '0':
            context['error'] = 'Выберите пациента'

            return render(request, 'mag/edit_medical_card.html', context)

        if not medical_card or not result or not diagnosis or not treatment:
            context['error'] = 'Заполните все поля'

            return render(request, 'mag/edit_medical_card.html', context)


        patient = Patient.objects.get(id=patient_id)

        electronic_card.medical_card = medical_card
        electronic_card.result = result
        electronic_card.diagnosis = diagnosis
        electronic_card.treatment = treatment

        electronic_card.save()

        patient.electronic_card = electronic_card

        patient.save()

        return redirect('medical_card_nurse')

    return render(request, 'mag/edit_medical_card.html', context)


def delete_medical_card(request, id):
    """
    Удаление медицинской карты медсестрой.

    Проверяет авторизацию и роль пользователя для удаления медицинской карты медсестрой.

    :param request: Объект запроса Django.
    :param id: Идентификатор медицинской карты для удаления.
    :return: Перенаправление на страницу входа или отображение страницы удаления медицинской карты медсестрой.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'nurse':
            return redirect('index')

    electronic_card = ElectronicCard.objects.get(id=id)
    electronic_card.delete()

    return redirect('medical_card_nurse')


def add_medical_card(request):
    """
    Добавление медицинской карты медсестрой.

    Проверяет авторизацию и роль пользователя для добавления медицинской карты медсестрой.

    :param request: Объект запроса Django.
    :return: Перенаправление на страницу входа или отображение страницы добавления медицинской карты медсестрой.
    """
    if not request.COOKIES.get('user_login'):
        return redirect('login')
    else:
        user = Role.objects.get(login=request.COOKIES.get('user_login'))

        if user.name != 'nurse':
            return redirect('index')

    patients = Patient.objects.all()

    context = {
        'patients': patients,
        'error': ''
    }

    if request.method == 'POST':
        medical_card = request.POST.get('medical_card')
        result = request.POST.get('result')
        diagnosis = request.POST.get('diagnosis')
        treatment = request.POST.get('treatment')
        patient_id = request.POST.get('patient')

        if patient_id == '0':
            context['error'] = 'Выберите пациента'

            return render(request, 'mag/add_medical_card.html', context)

        if not medical_card or not result or not diagnosis or not treatment:
            context['error'] = 'Заполните все поля'

            return render(request, 'mag/add_medical_card.html', context)

        patient = Patient.objects.get(id=patient_id)

        electronic_card = ElectronicCard()
        electronic_card.medical_card = medical_card
        electronic_card.result = result
        electronic_card.diagnosis = diagnosis
        electronic_card.treatment = treatment

        electronic_card.save()

        patient.electronic_card = electronic_card

        patient.save()

        return redirect('medical_card_nurse')

    return render(request, 'mag/add_medical_card.html', context)