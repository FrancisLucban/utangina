from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Debt, Payment
from .forms import DebtForm, PaymentForm, CustomUserCreationForm
from django.db.models import Q, F


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after registering
            messages.success(request, f'Welcome, {user.username}! Your account has been created')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    all_debts = request.user.debts.all()

    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'date_desc')

    if filter_type == 'owe':
        debts = all_debts.filter(debt_type='owe', is_settled=False)
    elif filter_type == 'owed':
        debts = all_debts.filter(debt_type='owed', is_settled=False)
    elif filter_type == 'settled':
        debts = all_debts.filter(is_settled=True)
    else:  # 'all'
        debts = all_debts.filter(is_settled=False)

    if search_query:
        debts = debts.filter(
            Q(person_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    sort_options = {
        'date_desc': '-date_set',
        'date_asc': 'date_set',
        'due_date_asc': F('due_date').asc(nulls_last=True),
        'due_date_desc': F('due_date').desc(nulls_last=True),
        'name_asc': 'person_name',
        'name_desc': '-person_name',
        'amount_desc': '-amount',
        'amount_asc': 'amount',
    }
    debts = debts.order_by(sort_options.get(sort_by, '-date_set'))

    # Totals and counts remain based on the FULL unsettled set, unaffected by which tab is active
    total_owe = sum(d.amount_remaining for d in all_debts.filter(debt_type='owe', is_settled=False))
    total_owed = sum(d.amount_remaining for d in all_debts.filter(debt_type='owed', is_settled=False))
    net_balance = total_owed - total_owe

    # Dashboard overdue and settled counts summary cards
    overdue_count = sum(1 for d in all_debts if d.is_overdue)
    due_soon_count = sum(1 for d in all_debts if d.is_due_soon)
    active_count = all_debts.filter(is_settled=False).count()
    settled_count = all_debts.filter(is_settled=True).count()

    # Pagination
    paginator = Paginator(debts, 10)
    page_number = request.GET.get('page')
    
    try:
        debts = paginator.page(page_number)
    except PageNotAnInteger:
        debts = paginator.page(1)
    except EmptyPage:
        debts = paginator.page(paginator.num_pages)

    return render(request, 'debts/dashboard.html', {
        'debts': debts,
        'filter_type': filter_type,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_owe': total_owe,
        'total_owed': total_owed,
        'net_balance': net_balance,
        'overdue_count': overdue_count,
        'due_soon_count': due_soon_count,
        'active_count': active_count,
        'settled_count': settled_count,
    })

@login_required
def debt_create(request):
    if request.method == 'POST':
        form = DebtForm(request.POST)
        if form.is_valid():
            debt = form.save(commit=False)
            debt.user = request.user
            debt.save()
            messages.success(request, f'Debt for {debt.person_name} added successfully!')
            return redirect('dashboard')
    else:
        form = DebtForm()
    return render(request, 'debts/debt_form.html', {'form': form, 'title': 'Add Debt'})


@login_required
def debt_edit(request, pk):
    debt = get_object_or_404(Debt, pk=pk, user=request.user)
    if request.method == 'POST':
        form = DebtForm(request.POST, instance=debt)
        if form.is_valid():
            form.save()
            messages.success(request, f'Debt for {debt.person_name} updated.')
            return redirect('dashboard')
    else:
        form = DebtForm(instance=debt)
    return render(request, 'debts/debt_form.html', {'form': form, 'title': 'Edit Debt'})


@login_required
def debt_delete(request, pk):
    debt = get_object_or_404(Debt, pk=pk, user=request.user)
    if request.method == 'POST':
        debt.delete()
        messages.success(request, f'Debt for {debt.person_name} deleted!')
        return redirect('dashboard')
    return render(request, 'debts/debt_confirm_delete.html', {'debt': debt})


@login_required
def debt_detail(request, pk):
    debt = get_object_or_404(Debt, pk=pk, user=request.user)
    payments = debt.payments.all().order_by('-date_paid')

    if request.method == 'POST':
        form = PaymentForm(request.POST, debt=debt)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.debt = debt
            payment.save()

            if debt.amount_remaining <= 0:
                debt.is_settled = True
                debt.save()
                messages.success(request, f'Payment recorded! {debt.person_name}\'s debt is now fully settled!')
            else:
                messages.success(request, 'Payment recorded!')

            return redirect('debt_detail', pk=debt.pk)
    else:
        form = PaymentForm()

    return render(request, 'debts/debt_detail.html', {
        'debt': debt,
        'payments': payments,
        'form': form,
    })