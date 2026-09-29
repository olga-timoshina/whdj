from django.contrib import admin
from django.urls import path

from core import views


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.index, name="index"),

    path("products/", views.products_list, name="products_list"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),

    path("warehouses/", views.warehouses_list, name="warehouses_list"),
    path("warehouses/<int:pk>/edit/", views.warehouse_edit, name="warehouse_edit"),
    path("warehouses/<int:pk>/delete/", views.warehouse_delete, name="warehouse_delete"),

    path("counterparties/", views.counterparties_list, name="counterparties_list"),
    path("counterparties/<int:pk>/edit/", views.counterparty_edit, name="counterparty_edit"),
    path("counterparties/<int:pk>/delete/", views.counterparty_delete, name="counterparty_delete"),

    path("docs/", views.docs_list, name="docs_list"),
    path("docs/create/", views.doc_create, name="doc_create"),
    path("docs/<int:pk>/", views.doc_detail, name="doc_detail"),
    path("docs/<int:pk>/edit/", views.doc_edit, name="doc_edit"),
    path("docs/<int:pk>/delete/", views.doc_delete, name="doc_delete"),
    path("docs/<int:pk>/post/", views.doc_post, name="doc_post"),

    path("items/<int:pk>/delete/", views.item_delete, name="item_delete"),

    path("stocks/", views.stocks_list, name="stocks_list"),
    path("ledger/", views.ledger_list, name="ledger_list"),
]