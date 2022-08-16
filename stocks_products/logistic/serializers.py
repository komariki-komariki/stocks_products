from rest_framework import serializers

from logistic.models import Product, StockProduct, Stock


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)
    class Meta:
        model = Stock
        fields = ['address', 'positions']

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)

        # заполнение связанной таблицы StockProduct
        for item in positions:
            StockProduct.objects.update_or_create(
                product=item['product'],
                price=item['price'],
                quantity=item['quantity'],
                stock=stock
            )
        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        # обновляем таблицу StockProduct
        for item in positions:
            StockProduct.objects.update_or_create(
                product=item['product'],
                stock=stock,
                defaults={
                    'price': item['price'],
                    'quantity': item['quantity'],
                    'stock': stock
                }
            )
        return stock