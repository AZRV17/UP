from django.urls import path, include

from mag import admin

from mag import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('reception', views.reception, name='reception'),
    path('users', views.users, name='users'),
    # path('notifications', views.notifications, name='notifications'),
    path('medical-card', views.medical_card, name='medical_card'),
    path('patient/delete/<int:id>', views.delete_patient, name='delete_patient'),
    path('doctor/delete/<int:id>', views.delete_doctor, name='delete_doctor'),
    path('nurse/delete/<int:id>', views.delete_nurse, name='delete_nurse'),
    path('doctor/edit/<int:id>', views.edit_doctor, name='edit_doctor'),
    path('patient/edit/<int:id>', views.edit_patient, name='edit_patient'),
    path('users/edit/<int:id>', views.edit_another_user, name='edit_user'),
    path('users/add_patient', views.add_patient, name='add_patient'),
    path('users/add_doctor', views.add_doctor, name='add_doctor'),
    path('users/add', views.add_another_user, name='add_user'),
    path('access_log', views.access_log, name='access_log'),
    path('calendar', views.calendar, name='calendar'),
    path('calendar/delete/<int:id>', views.delete_calendar, name='delete_calendar'),
    path('calendar/edit/<int:id>', views.edit_calendar, name='edit_calendar'),
    path('calendar/add', views.add_calendar, name='add_calendar'),
    path('reception_nurse', views.reception_nurse, name='reception_nurse'),
    path('medical_card_nurse', views.medical_card_nurse, name='medical_card_nurse'),
    path('medical_card/edit/<int:id>', views.edit_mediacal_card, name='edit_medical_card'),
    path('medical_card/delete/<int:id>', views.delete_medical_card, name='delete_medical_card'),
    path('medical_card/add', views.add_medical_card, name='add_medical_card'),
]