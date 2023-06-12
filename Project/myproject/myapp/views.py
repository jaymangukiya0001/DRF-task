from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import StockSerializer
import pandas as pd
import os


class StockListCreateView(generics.ListCreateAPIView):
    serializer_class = StockSerializer

    def get_queryset(self):
        # Read the Excel file and return the data
        try:
            df = pd.read_excel('stocks.xlsx')
            return df.to_dict('records')
        except FileNotFoundError:
            return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            action = serializer.validated_data.get("action")
            stock_price = serializer.validated_data.get("stock_price")
            quantity = serializer.validated_data.get("quantity")
            split_ratio = serializer.validated_data.get("split_ratio")
            df = pd.read_excel('./stocks.xlsx')
            df_final = pd.read_excel('./final.xlsx')
            average_buy_price, inventory= df_final.loc[:, ['average buy','inventory']].values.tolist()[0]
            if action == "BUY":
                average = (inventory*average_buy_price + stock_price*quantity)/(quantity+inventory)
                print(average)
                inventory += quantity
                df.loc[len(df.index)] = [action, stock_price, quantity] 
                df_final.loc[0] = {"average buy": average, "inventory": inventory}
                
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
            df_final.to_excel('./final.xlsx', index=False)
        # Append the new data to the Excel file
        # df = pd.DataFrame([serializer.validated_data])
        # with pd.ExcelWriter('stocks.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        #     df.to_excel(writer, index=False, sheet_name='Sheet1')


        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
