from django.contrib import admin
from .models import Debt, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1  # how many empty payment rows to show by default


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('person_name', 'phone_number', 'user', 'debt_type', 'amount', 'amount_remaining', 'is_settled', 'due_date', 'date_created', 'is_deleted')
    list_filter = ('debt_type', 'is_settled', 'date_created')
    search_fields = ('person_name', 'description', 'user__username')
    list_editable = ('is_settled',)
    date_hierarchy = 'date_created'
    inlines = [PaymentInline]
    ordering = ('-date_created',)
    actions = ['restore_selected', 'hard_delete_selected']

    def get_queryset(self, request):
        # Use all_objects so deleted rows are visible in admin (needed to restore them)
        return Debt.all_objects.all()

    @admin.action(description="Restore selected debts")
    def restore_selected(self, request, queryset):
        queryset.update(is_deleted=False, deleted_at=None)

    @admin.action(description="Permanently delete selected debts")
    def hard_delete_selected(self, request, queryset):
        for debt in queryset:
            debt.hard_delete()

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('debt', 'amount', 'date_paid', 'note')
    list_filter = ('date_paid',)
    search_fields = ('debt__person_name', 'note')
    ordering = ('-date_paid',)
    actions = ['restore_selected']

    def get_queryset(self, request):
        return Payment.all_objects.all()

    @admin.action(description="Restore selected payments")
    def restore_selected(self, request, queryset):
        queryset.update(is_deleted=False, deleted_at=None)