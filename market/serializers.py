from rest_framework import serializers

from market.models import Product, Order, Cart, Review


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'category', 'user')
        read_only_fields = ['user']  # Помечаем поле пользователя как только для чтения

    def create(self, validated_data):
        # Получаем текущего пользователя из запроса
        user = self.context['request'].user
        # Добавляем пользователя в данные перед сохранением
        validated_data['user'] = user
        # Создаем и возвращаем продукт
        return Product.objects.create(**validated_data)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'user', 'products', 'status', 'total_amount')
        read_only_fields = ('user',)

    def update(self, instance, validated_data):
        # Проверка разрешения на изменение заказа
        if not self.context['request'].user.is_staff:
            # Если пользователь не администратор, вызываем ошибку
            raise serializers.ValidationError("Вы не имеете прав на изменение этого заказа.")

        return super().update(instance, validated_data)

    def partial_update(self, instance, validated_data):
        # Проверка разрешения на частичное изменение заказа
        if not self.context['request'].user.is_staff:
            # Если пользователь не администратор, вызываем ошибку
            raise serializers.ValidationError("Вы не имеете прав на частичное изменение этого заказа.")

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        # Создаем и возвращаем продукт
        return Product.objects.create(**validated_data)


class CartSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username')
    products_names = serializers.SerializerMethodField()
    read_only_fields = ['user', 'user_name']  # Помечаем поле пользователя как только для чтения

    class Meta:
        model = Cart
        fields = ['id', 'user', 'user_name', 'products', 'products_names']

    def get_products_names(self, obj):
        return [product.name for product in obj.products.all()]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
