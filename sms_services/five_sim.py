import json
import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


class FiveSim:
    def __init__(self, purchase_id=None):
        load_dotenv()
        self._token = os.environ.get('FIVE_SIM_TOKEN')
        self._headers = {
            'Authorization': 'Bearer ' + self._token,
            'Accept': 'application/json',
        }

        self._proxies, _ = get_proxies()
        self._phone = None
        self._purchase_id = purchase_id
        with open('out_data.json') as json_file:
            self.prices = json.load(json_file)
        self.api_params_index = 0

    def check_price(self):
        params = (
            ('product', 'telegram'),
        )
        response = requests.get('https://5sim.net/v1/guest/prices',
                                headers=self._headers,
                                params=params,
                                proxies=self._proxies).json()

        df_marks = pd.DataFrame()
        for c, data in response[params[0][1]].items():
            for operator, data1 in data.items():
                price = data1['cost']
                count = data1['count']
                oper = operator
                new_row = {'country': c, 'price': price, 'oper': oper, 'count': count}
                df_marks = df_marks.append(new_row, ignore_index=True)

        df_marks = df_marks.sort_values('price', ascending=True)
        df_marks = df_marks.loc[df_marks['count'] != 0]
        df_marks = df_marks.loc[df_marks['price'] >= 10]

        df_marks.to_json(r'out_data.json', orient='records')

    def get_phone_by_id(self):
        response = requests.get(
            'https://5sim.net/v1/user/check/' + str(self._purchase_id),
            headers=self._headers,
            proxies=self._proxies
        )
        resp = response.json()
        print(resp)
        self._phone = resp.get('phone')
        return self._phone

    def get_number(self):
        price_data = self.prices[self.api_params_index]
        country = price_data['country']
        operator = price_data['oper']
        price = price_data['price']
        # country = 'china'
        # operator = 'virtual4'
        # price = '12.0'
        response = requests.get(
            'https://5sim.net/v1/user/buy/activation/' + country + '/' + operator + '/' + 'telegram',
            headers=self._headers,
            proxies=self._proxies
        )
        if response.text == 'no free phones':
            logger.debug(f'5ism info: country: {country}, operator: {operator}, price: {price} | no free phones!')
            self.api_params_index += 1
            self._phone = self.get_number()
        elif response.text == 'bad country':
            logger.debug(f'5ism info: country: {country}, operator: {operator}, price: {price} | bad country!')
            self.api_params_index += 1
            self._phone = self.get_number()
        else:
            logger.info(f'5ism info: country: {country}, operator: {operator}, price: {price} | good')
            print(response.text)
            resp = response.json()

            self._purchase_id = resp.get("id")
            self._phone = resp.get("phone")
            logger.info(f'Purchase: {resp["id"]} | Phone: {resp["phone"]}')
            return self._phone

    def get_sms(self):
        response = requests.get(
            'https://5sim.net/v1/user/check/' + str(self._purchase_id),
            headers=self._headers,
            proxies=self._proxies
        )
        resp = response.json()
        print(resp)
        all_messages = resp.get('sms')
        if len(all_messages) == 0:
            time.sleep(30)
            self.get_sms()
        message = resp.get("sms")[0]
        code = message.get("code")
        return code

    def cancel_order(self):
        response = requests.get(
            'https://5sim.net/v1/user/cancel/' + str(self._purchase_id),
            headers=self._headers,
            proxies=self._proxies
        )
        if response.text == 'order not found':
            logger.debug(f'5ism info: {self._purchase_id} | order not found')
        else:
            resp = response.json()
        logger.error(f"5ism info: {self._purchase_id} | order closed")
