from rest_framework import serializers

class StockSerializer(serializers.Serializer):
    # stock_name = serializers.CharField(max_length=100)
    action = serializers.CharField(max_length=5)
    quantity = serializers.IntegerField(required=False)
    stock_price = serializers.IntegerField(required=False)
    split_ratio = serializers.CharField(required=False, max_length=10)