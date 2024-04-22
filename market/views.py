from typing import Any, Dict, List, Union

from django.db.models import QuerySet
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from market.models import Product, Order, Cart, Review
from market.serializers import ProductSerializer, OrderSerializer, CartSerializer, ReviewSerializer
from market.permissions import IsOwnerOrReadOnly, IsSellerOrReadOnly, IsOwner


class ProductListCreate(generics.ListCreateAPIView):
    """
    API view to list and create products.

    Attributes:
        queryset: A queryset representing the collection of products.
        serializer_class: Serializer class for products.
        permission_classes: List of permission classes required for accessing this view.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSellerOrReadOnly]


class ProductDetail(generics.RetrieveAPIView):
    """
    API view to retrieve a single product.

    Attributes:
        queryset: A queryset representing the collection of products.
        serializer_class: Serializer class for products.
        permission_classes: List of permission classes required for accessing this view.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductRetrieveUpdateDestroyViewSet(viewsets.ModelViewSet):
    """
    API viewset to perform CRUD operations on products.

    Attributes:
        serializer_class: Serializer class for products.
        permission_classes: List of permission classes required for accessing this viewset.
    """

    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self) -> QuerySet:
        """
        Get the queryset of products.

        Returns:
            Union[List[Product], QuerySet]: The queryset of products.
        """
        user = self.request.user
        return Product.objects.filter(user=user)


class AddProductToCart(APIView):
    """
    View for adding a product to the cart.

    Attributes:
        request: The request object containing information about the request.
        product_id: The identifier of the product to add to the cart.
    """

    def post(self, request, product_id: int) -> Response:
        """
        Method to handle POST request for adding a product to the cart.

        Parameters:
            request (Request): The request object containing information about the request.
            product_id (int): The identifier of the product to add to the cart.

        Returns:
            Response: Response object indicating the result of the operation.
        """
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
    """
    View for retrieving and updating user's cart details.

    Attributes:
        serializer_class: Serializer class for cart objects.
        permission_classes: List of permission classes required for accessing this view.
    """

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self) -> Response:
        """
        Method to get the cart object associated with the current user.

        Returns:
            Cart: The cart object of the current user.
        """
        user = self.request.user
        if user.is_authenticated:
            try:
                cart = Cart.objects.get(user=user)
                return cart
            except Cart.DoesNotExist:
                return Response({'message': 'Cart does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


class CreateOrderFromCart(APIView):
    """
    View for creating an order from user's cart.

    Attributes:
        request: The request object containing information about the request.
    """

    def post(self, request) -> 'Response':
        """
        Method to handle POST request for creating an order from the user's cart.

        Parameters:
            request (Request): The request object containing information about the request.

        Returns:
            Response: Response object indicating the result of the operation.
        """
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'message': 'Cart does not exist'}, status=status.HTTP_404_NOT_FOUND)

        order = Order.objects.create(user=user, total_amount=0)
        total_amount = 0
        for product in cart.products.all():
            total_amount += product.price
            order.products.add(product)
        order.total_amount = total_amount
        order.save()

        cart.products.clear()

        return Response({'message': 'Order created successfully'}, status=status.HTTP_201_CREATED)


class CancelOrder(APIView):
    """
    View for cancelling an order.

    Attributes:
        request: The request object containing information about the request.
        order_id: The identifier of the order to be cancelled.
    """

    def post(self, request, order_id: int) -> Response:
        """
        Method to handle POST request for cancelling an order.

        Parameters:
            request (Request): The request object containing information about the request.
            order_id (int): The identifier of the order to be cancelled.

        Returns:
            Response: Response object indicating the result of the operation.
        """
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
    """
    View for creating a review for a product.

    Attributes:
        request: The request object containing information about the request.
        product_id: The identifier of the product for which the review is being created.
    """

    def post(self, request, product_id: int) -> Response:
        """
        Method to handle POST request for creating a review for a product.

        Parameters:
            request (Request): The request object containing information about the request.
            product_id (int): The identifier of the product for which the review is being created.

        Returns:
            Response: Response object indicating the result of the operation.
        """
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


class DeleteReviewView(generics.DestroyAPIView):
    """
    View for deleting a review for a product.

    Attributes:
        serializer_class: Serializer class for review objects.
        queryset: The queryset of review objects.
        permission_classes: List of permission classes required for accessing this view.
    """

    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        """
        Method to get the review object based on the review ID provided in the URL.

        Returns:
            Review: The review object to be deleted.
            Response: Response object indicating the result of the operation
        """
        try:
            review = Review.objects.get(id=self.kwargs['review_id'])
            self.check_object_permissions(self.request, review)
            return review
        except Review.DoesNotExist:
            return Response({'message': 'Review does not exist'}, status=status.HTTP_404_NOT_FOUND)
