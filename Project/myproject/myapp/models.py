from django.db import models

# Create your models here

class Stock(models.Model):
    # stock_name = serializers.CharField(max_length=100)
    action = models.CharField(max_length=5,blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    stock_price = models.IntegerField(blank=True, null=True)
    split_ratio = models.CharField(max_length=10,blank=True, null=True)

    def __str__(self):
        return f"Stock: {self.action} - Quantity: {self.quantity}  stock_price: {self.stock_price} "

class StockInfo(models.Model):
    average_buy = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    inventory = models.IntegerField(default=0)

    def __str__(self):
        return f"average_buy: {self.average_buy} - inventory: {self.inventory}"