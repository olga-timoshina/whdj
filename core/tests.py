from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from core.models import (
    Counterparty,
    MovementDoc,
    MovementItem,
    Product,
    Stock,
    StockLedger,
    Warehouse,
)

pytestmark = pytest.mark.django_db



#-------------------------------FIXTURES И ВСПОМОГАТЕЛЬНЫЕ ОБЪЕКТЫ-------------------------------#

@pytest.fixture
def doc_date_str():
    """
    Возвращает текущую дату и время в формате,
    подходящем для HTML-поля datetime-local

    Ожидаемый результат:
    строка формата YYYY-MM-DDTHH:MM
    """
    return timezone.localtime().strftime("%Y-%m-%dT%H:%M")


@pytest.fixture
def product():
    """
    Создает тестовый товар для сценариев TDD и PDD

    Ожидаемый результат:
    в базе появляется товар с ценой 1500.00
    """
    return Product.objects.create(
        sku="SKU-TDD-001",
        name="Товар TDD/PDD",
        unit="шт",
        price=Decimal("1500.00"),
    )


@pytest.fixture
def product_two():
    """
    Создает второй тестовый товар для многопозиционных документов

    Ожидаемый результат:
    в базе появляется второй товар с ценой 800.00
    """
    return Product.objects.create(
        sku="SKU-TDD-002",
        name="Товар второй",
        unit="шт",
        price=Decimal("800.00"),
    )


@pytest.fixture
def product_three():
    """
    Создает третий тестовый товар для многопозиционных документов

    Ожидаемый результат:
    в базе появляется третий товар с ценой 450.00
    """
    return Product.objects.create(
        sku="SKU-TDD-003",
        name="Товар третий",
        unit="шт",
        price=Decimal("450.00"),
    )


@pytest.fixture
def warehouse_from():
    """
    Создает склад-источник

    Ожидаемый результат:
    в базе появляется основной склад
    """
    return Warehouse.objects.create(
        name="Склад источник",
        address="Адрес 1",
    )


@pytest.fixture
def warehouse_to():
    """
    Создает склад-получатель

    Ожидаемый результат:
    в базе появляется второй склад
    """
    return Warehouse.objects.create(
        name="Склад получатель",
        address="Адрес 2",
    )


@pytest.fixture
def counterparty():
    """
    Создает тестового контрагента

    Ожидаемый результат:
    в базе появляется запись контрагента
    """
    return Counterparty.objects.create(
        name="ООО Процесс",
        contact_info="process@test.ru",
    )


def make_doc(doc_type, doc_no, warehouse_from=None, warehouse_to=None, counterparty=None):
    """
    Вспомогательная функция для быстрого создания документа движения

    Ожидаемый результат:
    создается документ движения с указанными реквизитами
    """
    return MovementDoc.objects.create(
        doc_type=doc_type,
        doc_no=doc_no,
        doc_date=timezone.now(),
        warehouse_from=warehouse_from,
        warehouse_to=warehouse_to,
        counterparty=counterparty,
        comment="Тестовый документ",
    )


def make_item(doc, product, quantity):
    """
    Вспомогательная функция для быстрого создания строки документа

    Ожидаемый результат:
    создается строка документа с автоматической подстановкой цены и суммы
    """
    return MovementItem.objects.create(
        doc=doc,
        product=product,
        quantity=Decimal(quantity),
    )

#-----------------TDD-ТЕСТЫ(ОДИН ТЕСТ = ОДНО БИЗНЕС-ПРАВИЛО ИЛИ ОДНО ОГРАНИЧЕНИЕ)-----------------#

class TestTDD:
    def test_01_reposting_document_does_not_change_stocks_twice(
        self,
        product,
        warehouse_to,
    ):
        """

        Что делает тест:
        - создает документ прихода;
        - добавляет строку;
        - проводит документ первый раз;
        - запоминает остаток и количество записей в журнале;
        - пытается провести документ повторно;
        - убеждается, что повторное проведение запрещено;
        - проверяет, что остаток и журнал не изменились.

        Ожидаемый результат:
        второй вызов post() вызывает ValidationError,
        остаток не увеличивается повторно, журнал не дублируется
        """
        doc = make_doc("receipt", "TDD-001", warehouse_to=warehouse_to)
        make_item(doc, product, "10")

        doc.post()

        stock = Stock.objects.get(warehouse=warehouse_to, product=product)
        stock_before = stock.quantity
        ledger_count_before = StockLedger.objects.filter(doc=doc).count()

        with pytest.raises(ValidationError):
            doc.post()

        stock.refresh_from_db()
        ledger_count_after = StockLedger.objects.filter(doc=doc).count()

        assert stock_before == Decimal("10.00")
        assert stock.quantity == Decimal("10.00")
        assert ledger_count_before == 1
        assert ledger_count_after == 1

    def test_02_transfer_with_same_source_and_destination_is_invalid(
        self,
        warehouse_from,
    ):
        """
        Что делает тест:
        - создает документ типа transfer;
        - задает одинаковый склад-источник и склад-получатель;
        - запускает валидацию документа;
        - проверяет, что возникла ошибка;
        - убеждается, что остатков и журнала нет.

        Ожидаемый результат:
        документ невалиден, проведение невозможно,
        движения по складу не формируются
        """
        doc = make_doc(
            "transfer",
            "TDD-002",
            warehouse_from=warehouse_from,
            warehouse_to=warehouse_from,
        )

        with pytest.raises(ValidationError):
            doc.full_clean()

        assert doc.is_posted is False
        assert Stock.objects.count() == 0
        assert StockLedger.objects.count() == 0

    def test_03_issue_without_source_warehouse_is_invalid(self):
        """
        Что делает тест:
        - создает документ типа issue без warehouse_from;
        - выполняет валидацию;
        - ожидает ошибку ValidationError.

        Ожидаемый результат:
        расходный документ без склада-источника считается невалидным
        """
        doc = make_doc("issue", "TDD-003")

        with pytest.raises(ValidationError):
            doc.full_clean()

        assert doc.is_posted is False

    def test_04_receipt_without_destination_warehouse_is_invalid(self):
        """
        Что делает тест:
        - создает документ типа receipt без warehouse_to;
        - выполняет валидацию;
        - ожидает ошибку;
        - проверяет, что остатки и журнал не создались.

        Ожидаемый результат:
        приходный документ без склада-получателя невалиден,
        никаких движений система не формирует
        """
        doc = make_doc("receipt", "TDD-004")

        with pytest.raises(ValidationError):
            doc.full_clean()

        assert doc.is_posted is False
        assert Stock.objects.count() == 0
        assert StockLedger.objects.count() == 0

    def test_05_item_with_zero_quantity_is_invalid(self, product, warehouse_to):
        """
        Что делает тест:
        - создает документ;
        - создает объект строки документа с quantity = 0;
        - запускает валидацию строки;
        - убеждается, что строка не сохраняется в базу.

        Ожидаемый результат:
        строка с нулевым количеством считается невалидной
        и не участвует в документе
        """
        doc = make_doc("receipt", "TDD-005", warehouse_to=warehouse_to)

        item = MovementItem(
            doc=doc,
            product=product,
            quantity=Decimal("0"),
        )

        with pytest.raises(ValidationError):
            item.full_clean()

        assert MovementItem.objects.count() == 0

    def test_06_item_with_negative_quantity_is_invalid(self, product, warehouse_to):
        """
        Что делает тест:
        - создает документ;
        - создает объект строки с quantity = -1;
        - запускает валидацию;
        - проверяет, что запись не сохраняется.

        Ожидаемый результат:
        строка с отрицательным количеством запрещена
        и не попадает в состав документа
        """
        doc = make_doc("receipt", "TDD-006", warehouse_to=warehouse_to)

        item = MovementItem(
            doc=doc,
            product=product,
            quantity=Decimal("-1"),
        )

        with pytest.raises(ValidationError):
            item.full_clean()

        assert MovementItem.objects.count() == 0

#-------------------PDD-ТЕСТЫ(СКВОЗНЫЕ ПРОЦЕССЫ И ПОЛЬЗОВАТЕЛЬСКИЕ СЦЕНАРИИ)-------------------#

class TestPDD:
    def test_07_full_process_receipt_then_partial_issue_keeps_expected_balance(
        self,
        client,
        product,
        warehouse_from,
        doc_date_str,
    ):
        """
        Что делает тест:
        - создает приходный документ через HTTP;
        - добавляет строку с товаром;
        - проводит приход;
        - создает расходный документ;
        - списывает часть количества;
        - проводит расход;
        - проверяет итоговый остаток;
        - проверяет записи журнала.

        Ожидаемый результат:
        остаток уменьшается до ожидаемого значения,
        в журнале зафиксированы и приход, и расход
        """
        receipt_create = client.post(
            reverse("doc_create"),
            data={
                "doc_type": "receipt",
                "doc_no": "PDD-001-R",
                "doc_date": doc_date_str,
                "warehouse_from": "",
                "warehouse_to": str(warehouse_from.pk),
                "counterparty": "",
                "comment": "Приход по процессу",
            },
        )
        assert receipt_create.status_code == 302

        receipt = MovementDoc.objects.get(doc_no="PDD-001-R")

        receipt_add_item = client.post(
            reverse("doc_detail", args=[receipt.pk]),
            data={
                "product": str(product.pk),
                "quantity": "10",
            },
        )
        assert receipt_add_item.status_code == 302

        receipt_post = client.get(reverse("doc_post", args=[receipt.pk]))
        assert receipt_post.status_code == 302

        issue_create = client.post(
            reverse("doc_create"),
            data={
                "doc_type": "issue",
                "doc_no": "PDD-001-I",
                "doc_date": doc_date_str,
                "warehouse_from": str(warehouse_from.pk),
                "warehouse_to": "",
                "counterparty": "",
                "comment": "Частичный расход",
            },
        )
        assert issue_create.status_code == 302

        issue = MovementDoc.objects.get(doc_no="PDD-001-I")

        issue_add_item = client.post(
            reverse("doc_detail", args=[issue.pk]),
            data={
                "product": str(product.pk),
                "quantity": "4",
            },
        )
        assert issue_add_item.status_code == 302

        issue_post = client.get(reverse("doc_post", args=[issue.pk]))
        assert issue_post.status_code == 302
        
        #----Перезагрузка модельного объекта в памяти----#
        receipt.refresh_from_db()
        issue.refresh_from_db()
        
        stock = Stock.objects.get(warehouse=warehouse_from, product=product)
        ledger_entries = StockLedger.objects.filter(product=product, warehouse=warehouse_from)

        assert stock.quantity == Decimal("6.00")
        assert receipt.is_posted is True
        assert issue.is_posted is True
        assert ledger_entries.count() == 2

    def test_08_full_process_receipt_then_overspend_is_rejected(
        self,
        product,
        warehouse_from,
    ):
        """
        Что делает тест:
        - создает и проводит приход на 6 единиц;
        - создает расход на 9 единиц;
        - пытается провести расход;
        - проверяет, что возникла ошибка;
        - убеждается, что остаток остался прежним;
        - убеждается, что лишняя запись в журнал не добавилась.

        Ожидаемый результат:
        приход остается проведенным, расход не проводится,
        остаток и журнал остаются корректными.
        """
        receipt = make_doc("receipt", "PDD-002-R", warehouse_to=warehouse_from)
        make_item(receipt, product, "6")
        receipt.post()

        ledger_before = StockLedger.objects.count()

        issue = make_doc("issue", "PDD-002-I", warehouse_from=warehouse_from)
        make_item(issue, product, "9")

        with pytest.raises(ValidationError):
            issue.post()

        stock = Stock.objects.get(warehouse=warehouse_from, product=product)
        ledger_after = StockLedger.objects.count()

        assert receipt.is_posted is True
        assert issue.is_posted is False
        assert stock.quantity == Decimal("6.00")
        assert ledger_before == 1
        assert ledger_after == 1

    def test_09_full_process_receipt_then_partial_transfer_to_second_warehouse(
        self,
        client,
        product,
        warehouse_from,
        warehouse_to,
        doc_date_str,
    ):
        """
        Что делает тест:
        - создает приход на первый склад;
        - проводит его;
        - создает документ перемещения;
        - переносит часть товара на второй склад;
        - проводит перемещение;
        - проверяет остатки на обоих складах;
        - проверяет журнал движений.

        Ожидаемый результат:
        на складе-источнике количество уменьшается,
        на складе-получателе увеличивается,
        журнал фиксирует обе стороны операции
        """
        receipt_create = client.post(
            reverse("doc_create"),
            data={
                "doc_type": "receipt",
                "doc_no": "PDD-003-R",
                "doc_date": doc_date_str,
                "warehouse_from": "",
                "warehouse_to": str(warehouse_from.pk),
                "counterparty": "",
                "comment": "Приход перед перемещением",
            },
        )
        assert receipt_create.status_code == 302

        receipt = MovementDoc.objects.get(doc_no="PDD-003-R")

        client.post(
            reverse("doc_detail", args=[receipt.pk]),
            data={"product": str(product.pk), "quantity": "9"},
        )
        client.get(reverse("doc_post", args=[receipt.pk]))

        transfer_create = client.post(
            reverse("doc_create"),
            data={
                "doc_type": "transfer",
                "doc_no": "PDD-003-T",
                "doc_date": doc_date_str,
                "warehouse_from": str(warehouse_from.pk),
                "warehouse_to": str(warehouse_to.pk),
                "counterparty": "",
                "comment": "Перемещение части товара",
            },
        )
        assert transfer_create.status_code == 302

        transfer = MovementDoc.objects.get(doc_no="PDD-003-T")

        transfer_add_item = client.post(
            reverse("doc_detail", args=[transfer.pk]),
            data={"product": str(product.pk), "quantity": "4"},
        )
        assert transfer_add_item.status_code == 302

        transfer_post = client.get(reverse("doc_post", args=[transfer.pk]))
        assert transfer_post.status_code == 302

        stock_from = Stock.objects.get(warehouse=warehouse_from, product=product)
        stock_to = Stock.objects.get(warehouse=warehouse_to, product=product)
        ledger_entries = StockLedger.objects.filter(doc=transfer, product=product)

        assert stock_from.quantity == Decimal("5.00")
        assert stock_to.quantity == Decimal("4.00")
        assert ledger_entries.count() == 2

    def test_10_full_process_multiline_document_creates_stocks_for_all_items(
        self,
        client,
        product,
        product_two,
        product_three,
        warehouse_from,
        doc_date_str,
    ):
        """
        Что делает тест:
        - создает один приходный документ;
        - добавляет в него три разные товарные строки;
        - проводит документ;
        - проверяет, что остатки создались по всем позициям;
        - проверяет цены и суммы строк;
        - проверяет количество записей журнала.

        Ожидаемый результат:
        все строки документа корректно участвуют в проводке,
        остатки и журнал формируются по каждой позиции
        """
        create_response = client.post(
            reverse("doc_create"),
            data={
                "doc_type": "receipt",
                "doc_no": "PDD-004-R",
                "doc_date": doc_date_str,
                "warehouse_from": "",
                "warehouse_to": str(warehouse_from.pk),
                "counterparty": "",
                "comment": "Многопозиционный документ",
            },
        )
        assert create_response.status_code == 302

        doc = MovementDoc.objects.get(doc_no="PDD-004-R")

        client.post(
            reverse("doc_detail", args=[doc.pk]),
            data={"product": str(product.pk), "quantity": "2"},
        )
        client.post(
            reverse("doc_detail", args=[doc.pk]),
            data={"product": str(product_two.pk), "quantity": "3"},
        )
        client.post(
            reverse("doc_detail", args=[doc.pk]),
            data={"product": str(product_three.pk), "quantity": "5"},
        )

        doc.refresh_from_db()
        assert doc.items.count() == 3

        items = list(doc.items.order_by("id"))
        assert items[0].price == Decimal("1500.00")
        assert items[0].line_total == Decimal("3000.00")
        assert items[1].price == Decimal("800.00")
        assert items[1].line_total == Decimal("2400.00")
        assert items[2].price == Decimal("450.00")
        assert items[2].line_total == Decimal("2250.00")

        post_response = client.get(reverse("doc_post", args=[doc.pk]))
        assert post_response.status_code == 302

        stock_1 = Stock.objects.get(warehouse=warehouse_from, product=product)
        stock_2 = Stock.objects.get(warehouse=warehouse_from, product=product_two)
        stock_3 = Stock.objects.get(warehouse=warehouse_from, product=product_three)

        assert stock_1.quantity == Decimal("2.00")
        assert stock_2.quantity == Decimal("3.00")
        assert stock_3.quantity == Decimal("5.00")
        assert StockLedger.objects.filter(doc=doc).count() == 3

    def test_11_posted_document_cannot_be_extended_with_new_items(
        self,
        client,
        product,
        product_two,
        warehouse_from,
        doc_date_str,
    ):
        """
        Что делает тест:
        - создает документ;
        - добавляет первую строку;
        - проводит документ;
        - пытается добавить вторую строку после проведения;
        - проверяет, что строка не добавилась.

        Ожидаемый результат:
        после проведения документ остается закрытым для расширения,
        количество строк не увеличивается
        """
        create_response = client.post(
            reverse("doc_create"),
            data={
                "doc_type": "receipt",
                "doc_no": "PDD-005-R",
                "doc_date": doc_date_str,
                "warehouse_from": "",
                "warehouse_to": str(warehouse_from.pk),
                "counterparty": "",
                "comment": "Документ для проверки запрета расширения",
            },
        )
        assert create_response.status_code == 302

        doc = MovementDoc.objects.get(doc_no="PDD-005-R")

        client.post(
            reverse("doc_detail", args=[doc.pk]),
            data={"product": str(product.pk), "quantity": "3"},
        )

        doc.refresh_from_db()
        assert doc.items.count() == 1

        client.get(reverse("doc_post", args=[doc.pk]))
        doc.refresh_from_db()
        assert doc.is_posted is True

        add_after_post_response = client.post(
            reverse("doc_detail", args=[doc.pk]),
            data={"product": str(product_two.pk), "quantity": "2"},
        )
        assert add_after_post_response.status_code == 302

        doc.refresh_from_db()
        assert doc.items.count() == 1
        assert MovementItem.objects.filter(doc=doc, product=product_two).count() == 0

    def test_12_invalid_document_process_stops_safely_and_creates_no_movements(
        self,
        client,
        warehouse_from,
        doc_date_str,
    ):
        """
        Что делает тест:
        - пытается создать документ перемещения с одинаковыми складами;
        - отправляет данные через HTTP POST;
        - проверяет, что форма не проходит валидацию;
        - проверяет, что документ не создан;
        - проверяет, что остатки и журнал не изменились.

        Ожидаемый результат:
        ошибочный процесс корректно останавливается на этапе создания документа,
        страница не уходит в редирект, а в системе не появляются ни документ,
        ни строки, ни остатки, ни записи журнала
        """
        response = client.post(
            reverse("doc_create"),
            data={
                "doc_type": "transfer",
                "doc_no": "PDD-006-T",
                "doc_date": doc_date_str,
                "warehouse_from": str(warehouse_from.pk),
                "warehouse_to": str(warehouse_from.pk),
                "counterparty": "",
                "comment": "Некорректное перемещение",
            },
        )

        assert response.status_code == 200
        assert MovementDoc.objects.filter(doc_no="PDD-006-T").count() == 0
        assert MovementItem.objects.count() == 0
        assert Stock.objects.count() == 0
        assert StockLedger.objects.count() == 0