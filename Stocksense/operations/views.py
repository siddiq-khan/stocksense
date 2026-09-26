from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Document
from .forms import ReceiptForm, DocumentLineForm
from .services import validate_receipt

#receipt section

@login_required
def receipt_list(request):
    status_filter = request.GET.get('status')
    receipts = Document.objects.filter(doc_type='receipt').order_by('-created_at')
    if status_filter:
        receipts = receipts.filter(status=status_filter)
    return render(request, 'operations/receipt_list.html', {
        'receipts': receipts,
        'status_choices': Document.Status.choices,
        'active_nav': 'receipts',
    })


@login_required
def receipt_create(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.doc_type = 'receipt'
            receipt.created_by = request.user
            receipt.save()
            messages.success(request, f"Draft receipt {receipt.reference} created.")
            return redirect('receipt_detail', pk=receipt.pk)
    else:
        form = ReceiptForm()
    return render(request, 'operations/receipt_form.html', {'form': form})


@login_required
def receipt_detail(request, pk):
    receipt = get_object_or_404(Document, pk=pk, doc_type='receipt')

    if request.method == 'POST':
        if 'add_line' in request.POST:
            line_form = DocumentLineForm(request.POST)
            if line_form.is_valid():
                line = line_form.save(commit=False)
                line.document = receipt
                line.save()
                return redirect('receipt_detail', pk=receipt.pk)
        elif 'validate' in request.POST:
            try:
                validate_receipt(receipt)
                messages.success(request, f"{receipt.reference} validated — stock updated.")
            except ValueError as e:
                messages.error(request, str(e))
            return redirect('receipt_detail', pk=receipt.pk)

    line_form = DocumentLineForm()
    return render(request, 'operations/receipt_detail.html', {
        'receipt': receipt,
        'line_form': line_form,
    })

#delivery section

from .forms import ReceiptForm, DeliveryForm, DocumentLineForm
from .services import validate_receipt, validate_delivery


@login_required
def delivery_list(request):
    status_filter = request.GET.get('status')
    deliveries = Document.objects.filter(doc_type='delivery').order_by('-created_at')
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    return render(request, 'operations/delivery_list.html', {
        'deliveries': deliveries,
        'status_choices': Document.Status.choices,
        'active_nav': 'receipts',
    })


@login_required
def delivery_create(request):
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.doc_type = 'delivery'
            delivery.created_by = request.user
            delivery.save()
            messages.success(request, f"Draft delivery {delivery.reference} created.")
            return redirect('delivery_detail', pk=delivery.pk)
    else:
        form = DeliveryForm()
    return render(request, 'operations/delivery_form.html', {'form': form})


@login_required
def delivery_detail(request, pk):
    delivery = get_object_or_404(Document, pk=pk, doc_type='delivery')

    if request.method == 'POST':
        if 'add_line' in request.POST:
            line_form = DocumentLineForm(request.POST)
            if line_form.is_valid():
                line = line_form.save(commit=False)
                line.document = delivery
                line.save()
                return redirect('delivery_detail', pk=delivery.pk)
        elif 'validate' in request.POST:
            try:
                validate_delivery(delivery)
                messages.success(request, f"{delivery.reference} validated — stock updated.")
            except ValueError as e:
                messages.error(request, str(e))
            return redirect('delivery_detail', pk=delivery.pk)

    line_form = DocumentLineForm()
    return render(request, 'operations/delivery_detail.html', {
        'delivery': delivery,
        'line_form': line_form,
    })

#transfer section

from .forms import ReceiptForm, DeliveryForm, TransferForm, DocumentLineForm
from .services import validate_receipt, validate_delivery, validate_internal_transfer


@login_required
def transfer_list(request):
    status_filter = request.GET.get('status')
    transfers = Document.objects.filter(doc_type='internal').order_by('-created_at')
    if status_filter:
        transfers = transfers.filter(status=status_filter)
    return render(request, 'operations/transfer_list.html', {
        'transfers': transfers,
        'status_choices': Document.Status.choices,
        'active_nav': 'receipts',
    })


@login_required
def transfer_create(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.doc_type = 'internal'
            transfer.created_by = request.user
            transfer.save()
            messages.success(request, f"Draft transfer {transfer.reference} created.")
            return redirect('transfer_detail', pk=transfer.pk)
    else:
        form = TransferForm()
    return render(request, 'operations/transfer_form.html', {'form': form})


@login_required
def transfer_detail(request, pk):
    transfer = get_object_or_404(Document, pk=pk, doc_type='internal')

    if request.method == 'POST':
        if 'add_line' in request.POST:
            line_form = DocumentLineForm(request.POST)
            if line_form.is_valid():
                line = line_form.save(commit=False)
                line.document = transfer
                line.save()
                return redirect('transfer_detail', pk=transfer.pk)
        elif 'validate' in request.POST:
            try:
                validate_internal_transfer(transfer)
                messages.success(request, f"{transfer.reference} validated — stock moved.")
            except ValueError as e:
                messages.error(request, str(e))
            return redirect('transfer_detail', pk=transfer.pk)

    line_form = DocumentLineForm()
    return render(request, 'operations/transfer_detail.html', {
        'transfer': transfer,
        'line_form': line_form,
    })

#adjustment section

from .forms import ReceiptForm, DeliveryForm, TransferForm, AdjustmentForm, DocumentLineForm, AdjustmentLineForm
from .services import validate_receipt, validate_delivery, validate_internal_transfer, validate_adjustment


@login_required
def adjustment_list(request):
    status_filter = request.GET.get('status')
    adjustments = Document.objects.filter(doc_type='adjustment').order_by('-created_at')
    if status_filter:
        adjustments = adjustments.filter(status=status_filter)
    return render(request, 'operations/adjustment_list.html', {
        'adjustments': adjustments,
        'status_choices': Document.Status.choices,
        'active_nav': 'receipts',
    })


@login_required
def adjustment_create(request):
    if request.method == 'POST':
        form = AdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.doc_type = 'adjustment'
            adjustment.created_by = request.user
            adjustment.save()
            messages.success(request, f"Draft adjustment {adjustment.reference} created.")
            return redirect('adjustment_detail', pk=adjustment.pk)
    else:
        form = AdjustmentForm()
    return render(request, 'operations/adjustment_form.html', {'form': form})


@login_required
def adjustment_detail(request, pk):
    adjustment = get_object_or_404(Document, pk=pk, doc_type='adjustment')

    if request.method == 'POST':
        if 'add_line' in request.POST:
            line_form = AdjustmentLineForm(request.POST)
            if line_form.is_valid():
                line = line_form.save(commit=False)
                line.document = adjustment
                line.save()
                return redirect('adjustment_detail', pk=adjustment.pk)
        elif 'validate' in request.POST:
            try:
                validate_adjustment(adjustment)
                messages.success(request, f"{adjustment.reference} validated — stock corrected.")
            except ValueError as e:
                messages.error(request, str(e))
            return redirect('adjustment_detail', pk=adjustment.pk)

    line_form = AdjustmentLineForm()
    return render(request, 'operations/adjustment_detail.html', {
        'adjustment': adjustment,
        'line_form': line_form,
    })

#cancel document view

from .services import validate_receipt, validate_delivery, validate_internal_transfer, validate_adjustment, cancel_document


@login_required
def document_cancel(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        try:
            cancel_document(document)
            messages.success(request, f"{document.reference} canceled.")
        except ValueError as e:
            messages.error(request, str(e))

    # Redirect back to the correct detail page based on doc_type
    redirect_map = {
        'receipt': 'receipt_detail',
        'delivery': 'delivery_detail',
        'internal': 'transfer_detail',
        'adjustment': 'adjustment_detail',
    }
    return redirect(redirect_map[document.doc_type], pk=document.pk)