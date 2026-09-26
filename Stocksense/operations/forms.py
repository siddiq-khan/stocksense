from django import forms
from .models import Document, DocumentLine

class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['warehouse', 'supplier_name']

class DocumentLineForm(forms.ModelForm):
    class Meta:
        model = DocumentLine
        fields = ['product', 'quantity']

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['warehouse', 'customer_name']

class TransferForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['source_warehouse', 'dest_warehouse']

class AdjustmentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['warehouse']


class AdjustmentLineForm(forms.ModelForm):
    class Meta:
        model = DocumentLine
        fields = ['product', 'counted_quantity']