from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    Counterparty,
    MovementDoc,
    MovementItem,
    Product,
    Stock,
    StockLedger,
    Warehouse,
)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["sku", "name", "unit", "price"]


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ["name", "address"]


class CounterpartyForm(forms.ModelForm):
    class Meta:
        model = Counterparty
        fields = ["name", "contact_info"]


class MovementDocForm(forms.ModelForm):
    doc_date = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = MovementDoc
        fields = [
            "doc_type",
            "doc_no",
            "doc_date",
            "warehouse_from",
            "warehouse_to",
            "counterparty",
            "comment",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk and not self.initial.get("doc_date"):
            self.initial["doc_date"] = timezone.localtime().strftime("%Y-%m-%dT%H:%M")

        if self.instance.pk and self.instance.doc_date:
            self.initial["doc_date"] = timezone.localtime(self.instance.doc_date).strftime(
                "%Y-%m-%dT%H:%M"
            )


class MovementItemForm(forms.ModelForm):
    class Meta:
        model = MovementItem
        fields = ["product", "quantity"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].required = True


def index(request):
    context = {
        "page": "home",
        "title": "Главная",
        "products_count": Product.objects.count(),
        "warehouses_count": Warehouse.objects.count(),
        "counterparties_count": Counterparty.objects.count(),
        "docs_count": MovementDoc.objects.count(),
        "posted_docs_count": MovementDoc.objects.filter(is_posted=True).count(),
        "recent_docs": MovementDoc.objects.select_related(
            "warehouse_from", "warehouse_to", "counterparty"
        )[:10],
        "stock_rows_count": Stock.objects.count(),
        "stock_total_qty": Stock.objects.aggregate(total=Sum("quantity"))["total"] or 0,
    }
    return render(request, "index.html", context)


def products_list(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар успешно добавлен.")
            return redirect("products_list")
    else:
        form = ProductForm()

    context = {
        "page": "products",
        "title": "Товары",
        "form": form,
        "objects": Product.objects.all(),
    }
    return render(request, "index.html", context)


def product_edit(request, pk):
    obj = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар успешно изменен.")
            return redirect("products_list")
    else:
        form = ProductForm(instance=obj)

    return render(
        request,
        "form.html",
        {
            "title": "Редактирование товара",
            "form": form,
            "cancel_url": "products_list",
        },
    )


def product_delete(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    try:
        obj.delete()
        messages.success(request, "Товар удален.")
    except ProtectedError:
        messages.error(request, "Нельзя удалить товар: он уже используется в документах.")
    return redirect("products_list")


def warehouses_list(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Склад успешно добавлен.")
            return redirect("warehouses_list")
    else:
        form = WarehouseForm()

    context = {
        "page": "warehouses",
        "title": "Склады",
        "form": form,
        "objects": Warehouse.objects.all(),
    }
    return render(request, "index.html", context)


def warehouse_edit(request, pk):
    obj = get_object_or_404(Warehouse, pk=pk)

    if request.method == "POST":
        form = WarehouseForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Склад успешно изменен.")
            return redirect("warehouses_list")
    else:
        form = WarehouseForm(instance=obj)

    return render(
        request,
        "form.html",
        {
            "title": "Редактирование склада",
            "form": form,
            "cancel_url": "warehouses_list",
        },
    )


def warehouse_delete(request, pk):
    obj = get_object_or_404(Warehouse, pk=pk)
    try:
        obj.delete()
        messages.success(request, "Склад удален.")
    except ProtectedError:
        messages.error(request, "Нельзя удалить склад: он уже используется в документах или остатках.")
    return redirect("warehouses_list")


def counterparties_list(request):
    if request.method == "POST":
        form = CounterpartyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Контрагент успешно добавлен.")
            return redirect("counterparties_list")
    else:
        form = CounterpartyForm()

    context = {
        "page": "counterparties",
        "title": "Контрагенты",
        "form": form,
        "objects": Counterparty.objects.all(),
    }
    return render(request, "index.html", context)


def counterparty_edit(request, pk):
    obj = get_object_or_404(Counterparty, pk=pk)

    if request.method == "POST":
        form = CounterpartyForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Контрагент успешно изменен.")
            return redirect("counterparties_list")
    else:
        form = CounterpartyForm(instance=obj)

    return render(
        request,
        "form.html",
        {
            "title": "Редактирование контрагента",
            "form": form,
            "cancel_url": "counterparties_list",
        },
    )


def counterparty_delete(request, pk):
    obj = get_object_or_404(Counterparty, pk=pk)
    try:
        obj.delete()
        messages.success(request, "Контрагент удален.")
    except ProtectedError:
        messages.error(request, "Нельзя удалить контрагента: он уже используется в документах.")
    return redirect("counterparties_list")


def docs_list(request):
    docs = MovementDoc.objects.select_related(
        "warehouse_from", "warehouse_to", "counterparty"
    ).all()

    context = {
        "page": "docs",
        "title": "Документы движения",
        "objects": docs,
    }
    return render(request, "index.html", context)


def doc_create(request):
    if request.method == "POST":
        form = MovementDocForm(request.POST)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.full_clean()
            doc.save()
            messages.success(request, "Документ создан. Теперь можно добавить строки.")
            return redirect("doc_detail", pk=doc.pk)
    else:
        form = MovementDocForm()

    return render(
        request,
        "form.html",
        {
            "title": "Создание документа",
            "form": form,
            "cancel_url": "docs_list",
        },
    )


def doc_edit(request, pk):
    doc = get_object_or_404(MovementDoc, pk=pk)

    if doc.is_posted:
        messages.error(request, "Проведенный документ редактировать нельзя.")
        return redirect("doc_detail", pk=doc.pk)

    if request.method == "POST":
        form = MovementDocForm(request.POST, instance=doc)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.full_clean()
            doc.save()
            messages.success(request, "Документ успешно изменен.")
            return redirect("doc_detail", pk=doc.pk)
    else:
        form = MovementDocForm(instance=doc)

    return render(
        request,
        "form.html",
        {
            "title": f"Редактирование документа #{doc.doc_no}",
            "form": form,
            "cancel_url": "doc_detail",
            "cancel_kwargs": {"pk": doc.pk},
        },
    )


def doc_delete(request, pk):
    doc = get_object_or_404(MovementDoc, pk=pk)

    if doc.is_posted:
        messages.error(request, "Проведенный документ удалять нельзя.")
        return redirect("doc_detail", pk=doc.pk)

    doc.delete()
    messages.success(request, "Документ удален.")
    return redirect("docs_list")


def doc_detail(request, pk):
    doc = get_object_or_404(
        MovementDoc.objects.select_related("warehouse_from", "warehouse_to", "counterparty"),
        pk=pk,
    )

    if request.method == "POST":
        if doc.is_posted:
            messages.error(request, "Нельзя добавлять строки в проведенный документ.")
            return redirect("doc_detail", pk=doc.pk)

        item_form = MovementItemForm(request.POST)
        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.doc = doc
            item.full_clean()
            item.save()
            messages.success(request, "Строка документа добавлена.")
            return redirect("doc_detail", pk=doc.pk)
    else:
        item_form = MovementItemForm()

        items = doc.items.select_related("product").all()
        ledger_entries = doc.ledger_entries.select_related("warehouse", "product").all()

        product_prices = {
            str(p.id): str(p.price)
            for p in Product.objects.all().order_by("name")
        }

        return render(
            request,
            "doc_detail.html",
            {
                "title": f"Документ #{doc.doc_no}",
                "doc": doc,
                "items": items,
                "item_form": item_form,
                "ledger_entries": ledger_entries,
                "product_prices": product_prices,
            },
        )


def item_delete(request, pk):
    item = get_object_or_404(MovementItem.objects.select_related("doc"), pk=pk)
    doc = item.doc

    if doc.is_posted:
        messages.error(request, "Нельзя удалять строки из проведенного документа.")
        return redirect("doc_detail", pk=doc.pk)

    item.delete()
    messages.success(request, "Строка документа удалена.")
    return redirect("doc_detail", pk=doc.pk)


def doc_post(request, pk):
    doc = get_object_or_404(MovementDoc, pk=pk)

    if doc.is_posted:
        messages.info(request, "Документ уже проведен.")
        return redirect("doc_detail", pk=doc.pk)

    try:
        doc.full_clean()
        doc.post()
        messages.success(request, "Документ успешно проведен.")
    except ValidationError as e:
        if hasattr(e, "messages"):
            messages.error(request, " ".join(e.messages))
        else:
            messages.error(request, str(e))

    return redirect("doc_detail", pk=doc.pk)


def stocks_list(request):
    stocks = Stock.objects.select_related("warehouse", "product").order_by(
        "warehouse__name", "product__name"
    )

    context = {
        "page": "stocks",
        "title": "Остатки",
        "objects": stocks,
    }
    return render(request, "index.html", context)


def ledger_list(request):
    entries = StockLedger.objects.select_related("doc", "warehouse", "product").all()[:200]

    context = {
        "page": "ledger",
        "title": "Журнал движений",
        "objects": entries,
    }
    return render(request, "index.html", context)