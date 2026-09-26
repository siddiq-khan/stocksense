from django.db import models
from django.conf import settings
from inventory.models import Product, Warehouse


class Document(models.Model):
    """Base for Receipt / Delivery / Internal Transfer / Adjustment."""

    class DocType(models.TextChoices):
        RECEIPT = 'receipt', 'Receipt'
        DELIVERY = 'delivery', 'Delivery'
        INTERNAL = 'internal', 'Internal Transfer'
        ADJUSTMENT = 'adjustment', 'Adjustment'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        WAITING = 'waiting', 'Waiting'
        READY = 'ready', 'Ready'
        DONE = 'done', 'Done'
        CANCELED = 'canceled', 'Canceled'

    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    reference = models.CharField(max_length=50, unique=True, blank=True)

    # For Receipt/Delivery/Adjustment: the single warehouse involved
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='documents',
                                   null=True, blank=True)
    # Only used for Internal Transfers
    source_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT,
                                          related_name='transfers_out', null=True, blank=True)
    dest_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT,
                                        related_name='transfers_in', null=True, blank=True)

    supplier_name = models.CharField(max_length=200, blank=True)   # for receipts
    customer_name = models.CharField(max_length=200, blank=True)   # for deliveries

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            prefix = {'receipt': 'RCV', 'delivery': 'DEL', 'internal': 'INT', 'adjustment': 'ADJ'}[self.doc_type]
            self.reference = f"{prefix}-{Document.objects.filter(doc_type=self.doc_type).count() + 1:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} ({self.get_status_display()})"


class DocumentLine(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    # Only used for Stock Adjustments — the physically counted quantity
    counted_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.product.sku} x {self.quantity}"


class StockLedger(models.Model):
    """Immutable audit trail — every stock movement, ever."""
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='ledger_entries')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='ledger_entries')
    change_qty = models.DecimalField(max_digits=12, decimal_places=2)  # +ve or -ve
    reason = models.CharField(max_length=20, choices=Document.DocType.choices)
    ref_document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, related_name='ledger_entries')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.name}: {self.change_qty:+} ({self.reason})"