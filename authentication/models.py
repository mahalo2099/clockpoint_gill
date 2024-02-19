from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Employee(models.Model):
    """Modelo para representar um funcionário."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=100, unique=False)

    def __str__(self):
        """Retorna a representação em string do funcionário."""
        username = getattr(self.user, 'username', 'No User')
        return f"{username} - Employee"


class AttendanceManager(models.Manager):
    """Gerenciador para manipular objetos de Attendance."""

    pass


class Attendance(models.Model):
    """Modelo para registrar a presença de um funcionário."""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        """Metadados para a classe Attendance."""
        app_label = "authentication"

    # objects = AttendanceManager()

    def __str__(self):
        """Retorna a representação em string do registro de presença."""
        username = getattr(self.employee.user, 'username', 'No User')
        return f"{username} - Attendance on {self.date}"

    def check_in_user(self):
        """Registra o horário de entrada do usuário."""
        if not self.check_in:  # Verifica se o check-in ainda não foi registrado
            self.check_in = timezone.now()
            self.save()
            return True  # Indica que o check-in foi registrado com sucesso
        return False  # Indica que o check-in já foi registrado anteriormente

    def check_out_user(self):
        """Registra o horário de saída do usuário."""
        if self.check_in and not self.check_out:
            # Verifica se o check-in foi feito e o check-out ainda não foi registrado
            self.check_out = timezone.now()
            self.save()
            return True  # Indica que o check-out foi registrado com sucesso
        return False  # Indica que o check-out já foi registrado anteriormente ou o check-in não foi feito

    def is_present(self):
        """Verifica se o usuário está presente."""
        return bool(self.check_in and not self.check_out)
