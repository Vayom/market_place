from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from market.models import Product, Order, Cart, Review
from market.serializers import ProductSerializer, OrderSerializer, CartSerializer
from market.permissions import IsOwnerOrReadOnly, IsSellerOrReadOnly, IsOwner


class ProductListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSellerOrReadOnly]


class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductRetrieveUpdateDestroyViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Product.objects.filter(user=user)


class AddProductToCart(APIView):
    def post(self, request, product_id):
        user = request.user
        if user.is_authenticated:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'message': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        cart = Cart.objects.get(user=user)
        cart.products.add(product)
        cart.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartDetail(generics.RetrieveUpdateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        user = self.request.user
        if user.is_authenticated:
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return Response({'message': 'Cart does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        return cart


class CreateOrderFromCart(APIView):
    def post(self, request):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'message': 'Cart does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Создаем заказ на основе товаров из корзины
        order = Order.objects.create(user=user, total_amount=0)
        total_amount = 0
        for product in cart.products.all():
            total_amount += product.price
            order.products.add(product)
        order.total_amount = total_amount
        order.save()

        # Очищаем корзину
        cart.products.clear()

        return Response({'message': 'Order created successfully'}, status=status.HTTP_201_CREATED)


class CancelOrder(APIView):
    def post(self, request, order_id):
        user = request.user
        if not user.is_authenticated:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            order = Order.objects.get(id=order_id)
            if order.status != 'Pending':
                return Response({'message': 'The order cannot be cancelled'})
        except Order.DoesNotExist:
            return Response({'message': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)
        if order.user != user:
            return Response({'message': 'Bad User'}, status=status.HTTP_404_NOT_FOUND)
        cart = Cart.objects.get(user=user)
        products = order.products.prefetch_related()

        for product in products:
            cart.products.add(product)
        cart.save()
        order.delete()
        serializer = CartSerializer(cart)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateReviewView(APIView):
    def post(self, request, product_id):
        user = request.user
        if not user.is_authenticated:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            product = Product.objects.get(id=product_id)
            text = request.data.get('text')
            rating = request.data.get('rating')
        except Product.DoesNotExist:
            return Response({'message': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except AttributeError:
            return Response({'message': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        review = Review.objects.create(user=user, product=product, text=text, rating=rating)
        return Response({'message': 'Review successfully'}, status=status.HTTP_201_CREATED)

