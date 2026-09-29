from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class Product(models.Model):
    sku = models.CharField("Артикул", max_length=50, unique=True)
    name = models.CharField("Наименование", max_length=255)
    unit = models.CharField("Единица измерения", max_length=20, default="шт")
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        db_table = "products"
        ordering = ["name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Warehouse(models.Model):
    name = models.CharField("Название склада", max_length=255, unique=True)
    address = models.CharField("Адрес", max_length=255, blank=True, default="")
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        db_table = "warehouses"
        ordering = ["name"]
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    def __str__(self):
        return self.name


class Counterparty(models.Model):
    name = models.CharField("Наименование контрагента", max_length=255, unique=True)
    contact_info = models.CharField("Контактная информация", max_length=255, blank=True, default="")
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        db_table = "counterparties"
        ordering = ["name"]
        verbose_name = "Контрагент"
        verbose_name_plural = "Контрагенты"

    def __str__(self):
        return self.name


class MovementDoc(models.Model):
    DOC_TYPES = [
        ("receipt", "Приход"),
        ("issue", "Расход"),
        ("transfer", "Перемещение"),
    ]

    doc_type = models.CharField("Тип документа", max_length=20, choices=DOC_TYPES)
    doc_no = models.CharField("Номер документа", max_length=50, unique=True)
    doc_date = models.DateTimeField("Дата документа", default=timezone.now)

    warehouse_from = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="out_docs",
        null=True,
        blank=True,
        verbose_name="Склад-отправитель",
    )
    warehouse_to = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="in_docs",
        null=True,
        blank=True,
        verbose_name="Склад-получатель",
    )
    counterparty = models.ForeignKey(
        Counterparty,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Контрагент",
    )

    comment = models.TextField("Комментарий", blank=True, default="")
    is_posted = models.BooleanField("Проведен", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        db_table = "movement_docs"
        ordering = ["-doc_date", "-id"]
        verbose_name = "Документ движения"
        verbose_name_plural = "Документы движения"

    def __str__(self):
        return f"{self.get_doc_type_display()} #{self.doc_no}"

    def clean(self):
        if self.doc_type == "receipt":
            if not self.warehouse_to:
                raise ValidationError("Для прихода нужно указать склад-получатель.")
        elif self.doc_type == "issue":
            if not self.warehouse_from:
                raise ValidationError("Для расхода нужно указать склад-отправитель.")
        elif self.doc_type == "transfer":
            if not self.warehouse_from or not self.warehouse_to:
                raise ValidationError("Для перемещения нужно указать оба склада.")
            if self.warehouse_from_id == self.warehouse_to_id:
                raise ValidationError("Склад-отправитель и склад-получатель должны различаться.")

    def post(self):
        if self.is_posted:
            raise ValidationError("Документ уже проведен.")

        items = list(self.items.select_related("product").all())
        if not items:
            raise ValidationError("Нельзя провести документ без строк.")

        with transaction.atomic():
            for item in items:
                qty = item.quantity
                product = item.product
                
                if product is None:
                    raise ValidationError("В документе есть строка с удаленным товаром. Проведение невозможно.")

                if qty <= 0:
                    raise ValidationError("Количество в строке должно быть больше нуля.")

                if self.doc_type == "receipt":
                    self._increase_stock(self.warehouse_to, product, qty)
                    StockLedger.objects.create(
                        doc=self,
                        product=product,
                        warehouse=self.warehouse_to,
                        delta_qty=qty,
                        note=f"Приход по документу {self.doc_no}",
                    )

                elif self.doc_type == "issue":
                    self._decrease_stock(self.warehouse_from, product, qty)
                    StockLedger.objects.create(
                        doc=self,
                        product=product,
                        warehouse=self.warehouse_from,
                        delta_qty=-qty,
                        note=f"Расход по документу {self.doc_no}",
                    )

                elif self.doc_type == "transfer":
                    self._decrease_stock(self.warehouse_from, product, qty)
                    self._increase_stock(self.warehouse_to, product, qty)

                    StockLedger.objects.create(
                        doc=self,
                        product=product,
                        warehouse=self.warehouse_from,
                        delta_qty=-qty,
                        note=f"Перемещение со склада {self.warehouse_from}",
                    )
                    StockLedger.objects.create(
                        doc=self,
                        product=product,
                        warehouse=self.warehouse_to,
                        delta_qty=qty,
                        note=f"Перемещение на склад {self.warehouse_to}",
                    )

            self.is_posted = True
            self.save(update_fields=["is_posted"])

    def _increase_stock(self, warehouse, product, qty):
        stock, _ = Stock.objects.select_for_update().get_or_create(
            warehouse=warehouse,
            product=product,
            defaults={"quantity": Decimal("0.00")},
        )
        stock.quantity += qty
        stock.save(update_fields=["quantity"])

    def _decrease_stock(self, warehouse, product, qty):
        stock, _ = Stock.objects.select_for_update().get_or_create(
            warehouse=warehouse,
            product=product,
            defaults={"quantity": Decimal("0.00")},
        )
        if stock.quantity < qty:
            raise ValidationError(
                f"Недостаточно остатка для товара '{product.name}' на складе '{warehouse.name}'."
            )
        stock.quantity -= qty
        stock.save(update_fields=["quantity"])


class MovementItem(models.Model):
    doc = models.ForeignKey(
        MovementDoc,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Документ",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Товар",
    )
    quantity = models.DecimalField("Количество", max_digits=12, decimal_places=2)
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField("Сумма", max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "movement_items"
        verbose_name = "Строка документа"
        verbose_name_plural = "Строки документов"

    def __str__(self):
        return f"{self.product or 'Удаленный товар'} x {self.quantity}"

    def clean(self):
        if self.product is None:
            raise ValidationError("Необходимо выбрать товар.")
        if self.quantity <= 0:
            raise ValidationError("Количество должно быть больше нуля.")
        if self.price < 0:
            raise ValidationError("Цена не может быть отрицательной.")
            
    def save(self, *args, **kwargs):
        if self.product_id:
            if hasattr(self, "product") and self.product:
                self.price = self.product.price
            else:
                self.price = Product.objects.only("price").get(pk=self.product_id).price

        self.line_total = (self.quantity or 0) * (self.price or 0)
        super().save(*args, **kwargs)


class Stock(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name="Склад",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар",
    )
    quantity = models.DecimalField("Остаток", max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "stocks"
        unique_together = ("warehouse", "product")
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"

    def __str__(self):
        return f"{self.warehouse} | {self.product} | {self.quantity}"


class StockLedger(models.Model):
    doc = models.ForeignKey(
        MovementDoc,
        on_delete=models.CASCADE,
        related_name="ledger_entries",
        verbose_name="Документ",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        verbose_name="Склад",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Товар",
    )
    delta_qty = models.DecimalField("Изменение количества", max_digits=12, decimal_places=2)
    created_at = models.DateTimeField("Дата записи", auto_now_add=True)
    note = models.CharField("Примечание", max_length=255, blank=True, default="")

    class Meta:
        db_table = "stock_ledger"
        ordering = ["-created_at", "-id"]
        verbose_name = "Журнал движения"
        verbose_name_plural = "Журнал движений"

    def __str__(self):
        product_name = self.product or "Удаленный товар"
        return f"{self.created_at:%Y-%m-%d %H:%M} | {product_name} | {self.delta_qty}"