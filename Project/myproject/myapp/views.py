from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import StockSerializer
from django.views.decorators.csrf import csrf_protect
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
                final_quantity = inventory - quantity
                rows = df.values.tolist()
                i=0
                s=0
                while True:
                    s += rows[i][-1]
                    if quantity>s:
                        quantity -= rows[i][-1]
                        rows[i][-1]=0
                        i+=1
                    else:
                        rows[i][-1] = rows[i][-1] - quantity
                        break
                for i in rows:
                    if i[-1] == 0:
                        rows.pop(0)

                average_buy_price = sum([b*c for a,b,c in rows])/final_quantity
                print(rows)        
                print(average_buy_price)
                del df
                df = pd.DataFrame(rows, columns=['action', 'stock_price', 'quantity'])
                df_final.loc[0] = {"average buy": average_buy_price, "inventory": inventory}

            elif action == "SPLIT":
                upper_part, lower_part = map(int, split_ratio.split(":"))
                rows = df.values.tolist()
                for i in range(len(rows)):
                    rows[i][-1] =  rows[i][-1]*(upper_part)/lower_part
                    rows[i][-2] =  rows[i][-2]*(lower_part)/upper_part
                average_buy_price = average_buy_price*lower_part/upper_part
                inventory = inventory*upper_part/lower_part
                del df
                df = pd.DataFrame(rows, columns=['action', 'stock_price', 'quantity'])
                df_final.loc[0] = {"average buy": average_buy_price, "inventory": inventory}
            df.to_excel('./stocks.xlsx', index=False)
            stock_info.save()
        # Append the new data to the Excel file
        # df = pd.DataFrame([serializer.validated_data])
        # with pd.ExcelWriter('stocks.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        #     df.to_excel(writer, index=False, sheet_name='Sheet1')


        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
