from datetime import datetime
from django.db.models import Count
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from authentication.models import Attendance, Employee
from gfg import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from .tokens import generate_token
from django.utils import timezone
from django.urls import reverse
from django.utils import timezone
from .models import Employee


# Create your views here.
def home(request):
    """Renderiza a página inicial."""
    return render(request, "authentication/index.html")


def signup(request):
    """Registra um novo usuário."""
    if request.method == "POST":
        username = request.POST.get("username")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        pass1 = request.POST.get("pass1")
        pass2 = request.POST.get("pass2")

        if User.objects.filter(username=username):
            messages.error(
                request, "Username already exist! please try some other username"
            )
            return redirect("home")

        if User.objects.filter(email=email):
            messages.error(request, "Email already registered!")
            return redirect("home")

        if len(username) > 10:
            messages.error(request, "Username should be less than 10 characters.")

        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!")

        if not username.isalnum():
            messages.error(
                request, "Username must contain only alphanumeric characters."
            )
            return redirect("home")

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = True
        myuser.save()

        # Cria um objeto Employee associado ao usuário recém-criado
        employee = Employee.objects.create(user=myuser)

        # Verifica se já existe um objeto Employee associado ao usuário
        employee, created = Employee.objects.get_or_create(user=myuser)

        # Welcome Email
        subject = "Welcome to GFG - Django Login"
        message = (
            "Hello "
            + myuser.first_name
            + "!! \n"
            + "Welcome to GFG!! \n Thank you for visiting our website \n  We have also sent you a confirmation email, please confirm your email address in order to activate your account. \n\n Thanking you\n Gill Correia"
        )
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirme your email @ GFG - Django Login!!"
        message2 = render_to_string(
            "email_confirmation.html",
            {
                "name": myuser.first_name,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(myuser.pk)),
                "token": generate_token.make_token(myuser),
            },
        )
        email = EmailMessage(
            email_subject, message2, settings.EMAIL_HOST_USER, [myuser.email]
        )
        email.fail_silently = True  # type: ignore
        email.send()

        return redirect("signin")

    return render(request, "authentication/signup.html")


def create_employee(request):
    """Após o registro do usuário, crie um Employee associado"""
    if request.method == "POST":
        user = request.user  # Obtém o usuário atualmente logado
        Employee.objects.create(user=user)


def example_view(request):
    """Verifica se o usuário está autenticado"""
    if request.user.is_authenticated:
        try:
            # Tenta obter o objeto Employee associado ao usuário
            employee = request.user.employee
        except Employee.DoesNotExist:
            # Se o objeto Employee não existir, você pode lidar com isso de acordo com suas necessidades
            messages.error(request, "User does not have an associated Employee object.")
            return HttpResponse("User does not have an associated Employee object.")

        # Agora você pode usar o objeto `employee` normalmente
        # ...

    else:
        # O usuário não está autenticado, você pode lidar com isso de acordo com suas necessidades
        messages.error(request, "User is not authenticated.")
        return HttpResponse("User is not authenticated.")

    # Restante da lógica da sua view...
    return render(request, "example_template.html", {"employee": employee})


def register_attendance(request):
    """Registra a presença de um funcionário."""
    try:
        employee = Employee.objects.get(user=request.user)
        attendance, created = Attendance.objects.get_or_create(
            employee=employee, date=timezone.now().date()
        )
    except Employee.DoesNotExist:
        messages.error(request, "Employee does not exist.")
        return HttpResponse("Employee does not exist.")

    try:
        attendance = Attendance.objects.get(
            employee=employee, date=timezone.now().date()
        )
    except Attendance.DoesNotExist:
        attendance = Attendance(employee=employee, date=timezone.now().date())

    if not attendance.check_in:
        attendance.check_in = timezone.now()
        attendance.save()
        messages.success(request, "Checked in sucessfully!")
    else:
        attendance.check_out = timezone.now()
        attendance.save()
        messages.success(request, "Checked out successfully!")

    return HttpResponse("Attendance registered successfully!")


def signin(request):
    """Realiza o login de um usuário."""
    if request.method == "POST":
        username = request.POST.get("username")
        pass1 = request.POST.get("pass1")
        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            # Verifique se o usuário autenticado tem um objeto Employee associado
            if hasattr(user, "employee"):
                employee = user.employee

                if "check_in" in request.POST:
                    try:
                        attendance = Attendance.objects.get(
                            employee=employee, date=timezone.now().date()  # type: ignore
                        )
                    except Attendance.DoesNotExist:
                        attendance = Attendance(
                            employee=employee, date=timezone.now().date()
                        )

                    if not attendance.check_in:
                        attendance.check_in = timezone.now()
                        attendance.save()

                elif "check_out" in request.POST:
                    try:
                        attendance = Attendance.objects.get(
                            employee=employee, date=timezone.now().date()
                        )
                        attendance.check_out = timezone.now()
                        attendance.save()
                    except Attendance.DoesNotExist:
                        messages.error(request, "Você não realizou o check-in hoje.")

                fname = user.first_name

                return render(
                    request, "authentication/registro_ponto.html", {"fname": fname}
                )

            else:
                # Caso não tenha um objeto Employee associado
                messages.error(
                    request, "User does not have an associated Employee object."
                )
                return redirect("home")

        else:
            messages.error(request, "Bad Credentials!")
            return redirect("home")

    return render(request, "authentication/signin.html")


def register_check_in(request):
    """Registra a entrada de um funcionário."""
    if request.method == "POST":
        user_request = request

        # Verifica se o usuário está autenticado e tem um objeto Employee associado
        if hasattr(user_request.user, "employee"):
            employee = user_request.user.employee

            today_attendance, created = Attendance.objects.get_or_create(
                employee=employee, date=timezone.now().date()
            )

            if not today_attendance.check_in:
                today_attendance.check_in = timezone.now()
                today_attendance.save()
                return JsonResponse(
                    {"success": True, "message": "Check-in registrado com sucesso"}
                )
            else:
                return JsonResponse(
                    {"success": False, "message": "Você já fez o check-in hoje"}
                )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Usuário não tem um objeto Employee associado",
                }
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Método de requisição inválido"}
        )


def register_check_out(request):
    """Registra a saída de um funcionário."""
    if request.method == "POST":
        user_request = request

        # Verifica se o usuário está autenticado e tem um objeto Employee associado
        if hasattr(user_request.user, "employee"):
            employee = user_request.user.employee

            try:
                today_attendance = Attendance.objects.get(
                    employee=employee, date=timezone.now().date()
                )
            except Attendance.DoesNotExist:
                return JsonResponse(
                    {"success": False, "message": "Você não realizou o check-in hoje"}
                )

            if not today_attendance.check_out:
                today_attendance.check_out = timezone.now()
                today_attendance.save()
                return JsonResponse(
                    {"success": True, "message": "Check-out registrado com sucesso"}
                )
            else:
                return JsonResponse(
                    {"success": False, "message": "Você já fez o check-out hoje"}
                )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Usuário não tem um objeto Employee associado",
                }
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Método de requisição inválido"}
        )


def monthly_report(request):
    """Exibe um relatório mensal de presenças."""
    # Obtém o mês e o ano atuais
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Obtem todos os funcionários
    employees = Employee.objects.all()

    # Lista para armazenar a presença de cada funcionário no mês atual
    presence_data = []
    print(presence_data)
    # Para cada funcionário, verifica se há presença em cada dia do mês atual
    for employee in employees:
        # Obtém as presenças do funcionário para o mês e ano atuais
        attendances = Attendance.objects.filter(
            employee=employee, date__year=current_year, date__month=current_month
        )

        # Verifica se o funcionário tem presença para cada dia do mês
        presence_for_month = [
            attendance.check_in is not None for attendance in attendances
        ]

        # Conta o número de dias que o funcionário esteve presente no mês atual
        days_present = sum(presence_for_month)

        # Adiciona os dados de presença do funcionário à lista
        presence_data.append(
            {
                "employee": employee,
                "days_present": days_present,
                "days_absent": len(presence_for_month) - days_present,
            }
        )

    return render(request, "monthly_report.html", {"presence_data": presence_data})


def signout(request):
    """Realiza o logout de um usuário."""
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect("home")


def activate(request, uidb64, token):
    """Ativa uma conta de usuário."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, "activation_failed.html")
