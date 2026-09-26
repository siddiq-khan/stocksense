from django.db import transaction
from django.utils import timezone
from inventory.models import StockItem
from .models import Document, StockLedger


def _apply_stock_change(product, warehouse, delta, reason, document):
    stock_item, _ = StockItem.objects.get_or_create(
        product=product, warehouse=warehouse, defaults={'quantity': 0}
    )
    stock_item.quantity += delta
    stock_item.save()
    StockLedger.objects.create(
        product=product, warehouse=warehouse,
        change_qty=delta, reason=reason, ref_document=document
    )


@transaction.atomic
def validate_receipt(document):
    for line in document.lines.select_related('product'):
        _apply_stock_change(line.product, document.warehouse, line.quantity, 'receipt', document)
    document.status = Document.Status.DONE
    document.validated_at = timezone.now()
    document.save()


@transaction.atomic
def validate_delivery(document):
    # Guard: block if any line would go negative
    for line in document.lines.select_related('product'):
        stock_item = StockItem.objects.filter(product=line.product, warehouse=document.warehouse).first()
        available = stock_item.quantity if stock_item else 0
        if available < line.quantity:
            raise ValueError(f"Insufficient stock for {line.product.sku}: have {available}, need {line.quantity}")

    for line in document.lines.select_related('product'):
        _apply_stock_change(line.product, document.warehouse, -line.quantity, 'delivery', document)
    document.status = Document.Status.DONE
    document.validated_at = timezone.now()
    document.save()


@transaction.atomic
def validate_internal_transfer(document):
    for line in document.lines.select_related('product'):
        _apply_stock_change(line.product, document.source_warehouse, -line.quantity, 'internal', document)
        _apply_stock_change(line.product, document.dest_warehouse, line.quantity, 'internal', document)
    document.status = Document.Status.DONE
    document.validated_at = timezone.now()
    document.save()


@transaction.atomic
def validate_adjustment(document):
    for line in document.lines.select_related('product'):
        stock_item = StockItem.objects.filter(product=line.product, warehouse=document.warehouse).first()
        system_qty = stock_item.quantity if stock_item else 0
        delta = line.counted_quantity - system_qty
        _apply_stock_change(line.product, document.warehouse, delta, 'adjustment', document)
    document.status = Document.Status.DONE
    document.validated_at = timezone.now()
    document.save()

def cancel_document(document):
    if document.status == Document.Status.DONE:
        raise ValueError("Cannot cancel a document that has already been validated.")
    document.status = Document.Status.CANCELED
    document.save()