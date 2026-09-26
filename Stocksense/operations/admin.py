from django.contrib import admin
from .models import Document, DocumentLine, StockLedger


class DocumentLineInline(admin.TabularInline):
    model = DocumentLine
    extra = 1


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'doc_type', 'status', 'warehouse', 'created_at')
    list_filter = ('doc_type', 'status', 'warehouse')
    inlines = [DocumentLineInline]


@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'change_qty', 'reason', 'timestamp')
    list_filter = ('reason', 'warehouse')
    readonly_fields = [f.name for f in StockLedger._meta.fields]  # ledger is audit-only, never hand-edited