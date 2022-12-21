import asyncio
from loguru import logger
from telethon import TelegramClient
from opentele.api import API
from sms_services import FiveSim
from telethon.errors.rpcerrorlist import PhoneNumberBannedError
from utils.errors import NoPhonesError
from utils.proxies import get_proxies

asyncio.set_event_loop(asyncio.SelectorEventLoop())
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class TelegramAutoreger:
    def __init__(self):
        self.client = None
        self.api = API.TelegramMacOS.Generate()
        self._proxies, self._telethon_proxies = get_proxies()

    async def register_account(self):
        fivesim_api = FiveSim(purchase_id=395344305)
        # phone = fivesim_api.get_phone_by_id()
        phone = fivesim_api.get_number()

        self.client = TelegramClient(phone, api_id=self.api.api_id, api_hash=self.api.api_hash)
        await self.client.connect()
        try:
            await self.client.send_code_request(phone)
        except PhoneNumberBannedError:
            fivesim_api.cancel_order()
            logger.error(PhoneNumberBannedError)


if __name__ == '__main__':
    f = TelegramAutoreger()
    # five = FiveSim(purchase_id=395335571)
    try:
        asyncio.run(f.register_account())
    except NoPhonesError:
        print('no phones')
    # code = five.get_sms()
    # print(code)
