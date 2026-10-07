from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from datetime import timedelta
from .utils import generate_uuid7

class SoftDeleteManager(models.Manager):
    """Default manager, excludes soft-deleted records automatically."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager() # used everywhere by default (views, related managers)
    all_objects = models.Manager() # used only when we explicitly want deleted rows too (admin)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """Soft delete: just flag it, don't actually remove the row"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, *args, **kwargs):
        """Escape hatch for permanently removing a row, if ever needed"""
        super().delete(*args, **kwargs)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()


class Debt(SoftDeleteModel):
    DEBT_TYPES = [
        ('owe', 'I owe someone'),
        ('owed', 'Someone owes me'),
    ]

    id = models.UUIDField(primary_key=True, default=generate_uuid7, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='debts')
    person_name = models.CharField(max_length=100)
    phone_number = PhoneNumberField(blank=True)
    debt_type = models.CharField(max_length=4, choices=DEBT_TYPES, default='owe')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    date_set = models.DateField(default=timezone.localdate, help_text="When this debt actually happened")
    date_created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    is_settled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.person_name} - {self.amount}"

    @property
    def amount_remaining(self):
        paid = sum(p.amount for p in self.payments.all())
        return self.amount - paid

    @property
    def is_overdue(self):
        if self.is_settled or not self.due_date:
            return False
        return self.due_date < timezone.now().date()

    @property
    def is_due_soon(self):
        if self.is_settled or not self.due_date or self.is_overdue:
            return False
        return self.due_date <= timezone.now().date() + timedelta(days=3)


class Payment(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid7, editable=False)
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateField(default=timezone.localdate)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.debt.person_name}"
