from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import StockSerializer
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from .models import Stock, StockInfo
import pandas as pd
import os


class StockListCreateView(generics.ListCreateAPIView):
    serializer_class = StockSerializer

    def get_queryset(self):
        # Read the Excel file and return the data
        return Stock.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # day = request.data.get("day")
            action = request.data.get("action")
            stock_price = request.data.get("stock_price")
            quantity = request.data.get("quantity")
            split_ratio = request.data.get("split_ratio")
            
            df = pd.read_excel('./stocks.xlsx')
            stock_info, _ = StockInfo.objects.get_or_create(id=1)
            average_buy_price = stock_info.average_buy
            inventory = stock_info.inventory
            if action == "BUY":
                average = (inventory*average_buy_price + stock_price*quantity)/(quantity+inventory)
                print(average)
                inventory += quantity
                stock_info.average_buy = average
                stock_info.inventory = inventory
                new_stock = Stock(action=action, quantity=quantity, stock_price=stock_price)
                new_stock.save()
                print(stock_info, new_stock)
                
            elif action == "SELL":
                print("sell")
                final_quantity = int(inventory) - int(quantity)
                data = Stock.objects.all()
                rows = [[getattr(instance, field.name) for field in Stock._meta.fields] for instance in data]
                print(rows)
                i=0
                s=0
                while i<len(rows):
                    if rows[i][1]=="BUY":
                        s += rows[i][-2]
                        if quantity>s:
                            quantity -= rows[i][-2]
                            rows[i][-2]=0
                            i+=1
                        else:
                            rows[i][-2] = rows[i][-2] - quantity
                            break
                    else:
                        i+=1
                for i in rows:
                    if i[-2] == 0 and i[1] == "BUY":
                        rows.pop(0)

                total_sum = 0
                for row in rows:
                    if rows[1]=="BUY":
                        total_sum+=row[2] * row[3]
                    
                average_buy_price = total_sum/final_quantity
                print(rows)        
                print(average_buy_price)
                with transaction.atomic():
                    Stock.objects.all().delete()  # Clear the existing data in the table
                    for row in rows:
                        obj = Stock()
                        try:
                            obj.day = row[0]
                            obj.action = row[1]
                            obj.stock_price = row[2] if row[2] else None
                            obj.quantity = row[3] if row[3] else None
                            obj.split_ratio = row[4] if row[4] else None
                            obj.save()
                        except Exception:
                            obj.save()

                stock_info.average_buy = average_buy_price
                stock_info.inventory = final_quantity
                new_stock = Stock(action=action, quantity=quantity)
                new_stock.save()

            elif action == "SPLIT":
                upper_part, lower_part = map(int, split_ratio.split(":"))
                data = Stock.objects.all()
                rows = [[getattr(instance, field.name) for field in Stock._meta.fields] for instance in data]
                print(rows)
                for i in range(len(rows)):
                    if rows[i][1]=="BUY":
                        rows[i][-2] =  int(rows[i][-2])*(upper_part)/lower_part
                        rows[i][-3] =  int(rows[i][-3])*(lower_part)/upper_part
                average_buy_price = average_buy_price*lower_part/upper_part
                inventory = inventory*upper_part/lower_part
                stock_info.average_buy = average_buy_price
                stock_info.inventory = inventory
                with transaction.atomic():
                    Stock.objects.all().delete()  # Clear the existing data in the table
                    for row in rows:
                        obj = Stock()
                        try:
                            obj.day = row[0]
                            obj.action = row[1]
                            obj.stock_price = row[2] if row[2] else None
                            obj.quantity = row[3] if row[3] else None
                            obj.split_ratio = row[4] if row[4] else None
                            obj.save()
                        except Exception:
                            obj.save()
                new_stock = Stock(action=action, split_ratio=split_ratio)
                new_stock.save()
            stock_info.save()
        # Append the new data to the Excel file
        # df = pd.DataFrame([serializer.validated_data])
        # with pd.ExcelWriter('stocks.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        #     df.to_excel(writer, index=False, sheet_name='Sheet1')


        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
