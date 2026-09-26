from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, Sum,F, Q
from inventory.models import Product, StockItem
from operations.models import Document
from django.db.models.functions import Coalesce
from decimal import Decimal




@login_required
def dashboard_view(request):
    # --- KPIs ---
    total_products = Product.objects.count()

    # Low stock: total quantity across all warehouses for a product falls at/below its reorder point
    low_stock_products = (
        Product.objects
        .annotate(total_qty=Coalesce(Sum('stock_items__quantity'), Decimal('0'), output_field=DecimalField()))
        .filter(total_qty__lte=F('reorder_point'))
    )
    low_stock_count = low_stock_products.count()
    out_of_stock_count = low_stock_products.filter(total_qty__lte=0).count()

    pending_receipts = Document.objects.filter(doc_type='receipt').exclude(status__in=['done', 'canceled']).count()
    pending_deliveries = Document.objects.filter(doc_type='delivery').exclude(status__in=['done', 'canceled']).count()
    scheduled_transfers = Document.objects.filter(doc_type='internal').exclude(status__in=['done', 'canceled']).count()

    # --- Dynamic filters ---
    documents = Document.objects.all().order_by('-created_at')

    doc_type = request.GET.get('doc_type')
    status = request.GET.get('status')
    warehouse_id = request.GET.get('warehouse')

    if doc_type:
        documents = documents.filter(doc_type=doc_type)
    if status:
        documents = documents.filter(status=status)
    if warehouse_id:
        documents = documents.filter(
            Q(warehouse_id=warehouse_id) | Q(source_warehouse_id=warehouse_id) | Q(dest_warehouse_id=warehouse_id)
        )

    from inventory.models import Warehouse
    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'pending_receipts': pending_receipts,
        'pending_deliveries': pending_deliveries,
        'scheduled_transfers': scheduled_transfers,
        'documents': documents,
        'doc_type_choices': Document.DocType.choices,
        'status_choices': Document.Status.choices,
        'warehouses': Warehouse.objects.all(),
        'selected_doc_type': doc_type,
        'selected_status': status,
        'selected_warehouse': warehouse_id,
    }
    return render(request, 'dashboard/dashboard.html', context)