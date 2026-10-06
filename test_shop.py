import pytest
from shop import Order, OrderService, PaymentGateway, CONFIG

def test_process_order_with_mocked_gateway(monkeypatch):
    """
    CP-01: Simulación del servicio de pagos usando monkeypatch.setattr().
    Cubre RF-10, RF-11 y RF-14.
    """
    # Sustitución del método charge de PaymentGateway
    def mock_charge(self, amount):
        return {"status": "approved", "amount": amount}

    monkeypatch.setattr(PaymentGateway, "charge", mock_charge)

    products = [
        {"name": "Teclado", "price": 800, "quantity": 1},
        {"name": "Mouse", "price": 300, "quantity": 1}
    ]
    order = Order(products)
    service = OrderService(CONFIG)

    order_processed = service.process_order(order)
    result = order_processed["order"]

    assert order_processed["payment"]["status"] == "approved"
    assert order_processed["payment"]["amount"] == 1148.4
    assert result["subtotal"] == 1100
    assert result["discount"] == 110.0
    assert result["tax"] == 158.4
    assert result["total"] == 1148.4


def test_order_with_modified_tax_rate(monkeypatch):
    """
    CP-02: Modificación temporal de la configuración global usando monkeypatch.setitem().
    Cubre RF-07, RF-08 y RF-09.
    """
    # Modificación temporal del impuesto al 8%
    monkeypatch.setitem(CONFIG, "tax_rate", 0.08)

    products = [
        {"name": "Monitor", "price": 600, "quantity": 1}
    ]
    order = Order(products)
    service = OrderService(CONFIG)

    result = service.calculate_total(order)

    # Subtotal = 600, Descuento 5% = 30, Base = 570, Impuesto (8%) = 45.6, Total = 615.6
    assert result["subtotal"] == 600
    assert result["discount"] == 30.0
    assert result["tax"] == 45.6
    assert result["total"] == 615.6


def test_order_without_discount_service(monkeypatch):
    """
    CP-03: Eliminación del servicio de descuentos usando monkeypatch.delattr().
    Cubre RF-12 y RF-13.
    """
    products = [
        {"name": "Laptop", "price": 1200, "quantity": 1}
    ]
    order = Order(products)
    service = OrderService(CONFIG)

    # Eliminación temporal del atributo discount_service en la instancia
    monkeypatch.delattr(service, "discount_service", raising=False)

    result = service.calculate_total(order)

    # Al no haber servicio de descuento, discount = 0
    # Subtotal = 1200, Descuento = 0, Impuesto (16%) = 192.0, Total = 1392.0
    assert result["subtotal"] == 1200
    assert result["discount"] == 0
    assert result["tax"] == 192.0
    assert result["total"] == 1392.0