# from django.db import models
# from django.contrib.auth.models import AbstractUser
#
# # Custom User
# class User(AbstractUser):
#     phone = models.CharField(max_length=20, unique=True)
#
#     def __str__(self):
#         return self.username
#
#
# #  Filial (branch)
# class Branch(models.Model):
#     name = models.CharField(max_length=255)
#     address = models.TextField()
#
#     def __str__(self):
#         return self.name
#
#
# #  Xizmat (service)
#
# class Service(models.Model):
#     branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="services")
#     name = models.CharField(max_length=255)
#     duration = models.PositiveIntegerField(help_text="Xizmat davomiyligi (minutda)")
#
#     def __str__(self):
#         return f"{self.name} ({self.branch.name})"
#
#
# #  Queue (navbat)
#
# class Queue(models.Model):
#     STATUS_CHOICES = (
#         ('waiting', 'Waiting'),
#         ('active', 'Active'),
#         ('done', 'Done'),
#         ('cancelled', 'Cancelled'),
#     )
#
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="queues")
#     service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="queues")
#     branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="queues")
#
#     number = models.PositiveIntegerField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     started_at = models.DateTimeField(null=True, blank=True)
#     finished_at = models.DateTimeField(null=True, blank=True)
#
#     class Meta:
#         ordering = ['number']
#         unique_together = ('service', 'branch', 'number')
#
#     def __str__(self):
#         return f"{self.branch.name} - {self.service.name} - #{self.number}"


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import transaction


class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.username or self.phone


class Branch(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

    class Meta:
        verbose_name = 'Filial'
        verbose_name_plural = 'Filiallar'

    def __str__(self):
        return self.name


class Service(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    duration = models.PositiveIntegerField(help_text='Xizmat davomiyligi (minutda)')

    class Meta:
        verbose_name = 'Xizmat'
        verbose_name_plural = 'Xizmatlar'

    def __str__(self):
        return f'{self.name} ({self.branch.name})'


class Queue(models.Model):
    STATUS_CHOICES = (
        ('waiting', 'Kutilmoqda'),
        ('active', 'Jarayonda'),
        ('done', 'Tugallangan'),
        ('cancelled', 'Bekor qilingan'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='queues')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='queues')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='queues')

    number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['number']
        verbose_name = 'Navbat'
        verbose_name_plural = 'Navbatlar'
        # unique_together olib tashlandi - chunki har bir filial/xizmat uchun alohida raqamlash kerak
        constraints = [
            models.UniqueConstraint(fields=['service', 'branch', 'number'], name='unique_queue_number')
        ]

    def __str__(self):
        return f'{self.branch.name} - {self.service.name} - #{self.number}'

    @staticmethod
    @transaction.atomic
    def get_next_number(service, branch):
        """Thread-safe raqam berish funksiyasi"""
        from django.db.models import Max
        last = Queue.objects.filter(
            service=service,
            branch=branch
        ).aggregate(max_num=Max('number'))['max_num']
        return (last or 0) + 1