from rest_framework import serializers
from .models import Stock, StockInfo

class StockSerializer(serializers.Serializer):
    class Meta:
        model = Stock
        fields = '__all__'


class StockInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockInfo
        fields = ('average_buy', 'inventory')