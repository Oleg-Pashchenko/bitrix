import asyncio
import time

from aiohttp import ClientResponseError
from fast_bitrix24 import Bitrix
from dataclasses import dataclass
import datetime
import gpt


@dataclass()
class Message:
    chat_id: str
    text: str
    title: str


class BitrixAvatarex:
    def __init__(self, webhook: str):
        self.bitrix: Bitrix = Bitrix(webhook, verbose=False)

    def get_unanswered_messages(self):
        chat_list = self.bitrix.get_all(method='im.recent.get')
        arr = []
        for chat in chat_list:

            try:
                lead_id = int(str(chat).split('LEAD|')[1].split('|')[0])
            except:
                continue
            status = self.get_deal(lead_id)['STATUS_ID']
            if status not in ['NEW', 'PROCESSED', 'IN_PROCESS', '1', 'CONVERTED']:
                continue
            if 'chat' in chat.keys() and chat['chat'].get('role', None) != 'MEMBER' and chat['message'][
                'status'] == 'received' and chat['type'] == 'chat':
                print(f'[Новое сообщение] {chat["id"]}: {chat["title"]} - {chat["message"]["text"]}')
                arr.append(Message(chat_id=chat['id'], title=chat['title'], text=chat['message']['text']))
        return arr

    def send_message(self, message: Message, answer: str):
        message_id = self.bitrix.call(method='im.message.add', items={
            'DIALOG_ID': message.chat_id,
            'MESSAGE': answer
        })
        print(
            f'[Отправлено сообщение (id: {message_id})] На сообщение <{message.text}> от <{message.title}> отправлен ответ <{answer}>')
        return message_id

    def is_connection_success(self) -> bool:
        """Returns connection status"""
        try:
            self.bitrix.get_all(method='im.recent.get')
        except ClientResponseError:
            return False
        return True

    def get_info(self):
        pipelines = self.bitrix.get_all(method='crm.category.list', params={
            'entityTypeId': 2
        })  # Получение воронок
        print('Воронки:')
        for pipeline in pipelines:
            print('Воронка:', pipeline['id'], pipeline['name'])
            stages = self.bitrix.get_all(method='crm.dealcategory.stage.list', params={
                'id': pipeline['id']
            })
            print('Стадии:')
            for stage in stages:
                print(stage['STATUS_ID'], stage['NAME'])
        fields = self.bitrix.call(method='crm.deal.fields', items={
            'order': {
                'ID': 'desc'
            }
        })

        print('Поля:')
        for f in fields.keys():
            if 'UF_CRM_' in f:
                print(fields[f]['listLabel'], fields[f]['title'])

    def fill_field(self):
        response = self.bitrix.call(method='crm.deal.update', items={
            'id': 1,
            'fields': {
                'UF_CRM_1703537943067': 'я обновил'
            }
        })
        print(response)

    def get_deal(self, deal_id):
        response = self.bitrix.call(method='crm.lead.get', items={
            'id': deal_id
        })
        return response


async def execute():
    while True:
        webhook_test = 'https://avatarex.bitrix24.ru/rest/42/eg712ozo8h3634fj/'
        webhook_test = 'https://solutionpro.bitrix24.ru/rest/26447/jgdhsezzfqewow7k/'
        webhook_test = 'https://solutionpro.bitrix24.ru/rest/26447/b18f6vmj69dpikl9/'
        bitrix_avatarex = BitrixAvatarex(webhook=webhook_test)
        print('подключаюсь')

        connection_status: bool = bitrix_avatarex.is_connection_success()
        # print(connection_status)
        # print(bitrix_avatarex.get_info())
        # exit(0) # C1:FINAL_INVOICE Не дозвонились
        # C1:PREPAYMENT_INVOICE В работе
        #

        if not connection_status:
            return

        messages: list[Message] = bitrix_avatarex.get_unanswered_messages()
        for message in messages:
            answer, thread = await gpt.execute(message.text, assistant_id='asst_WdMb0jXCuZgX9qN2W3zihFHl')
            print(f'[ОТВЕТ] {answer}')
            bitrix_avatarex.send_message(message, answer)
        # bitrix_avatarex.fill_field()
        # bitrix_avatarex.get_fields_by_deal_id()
        time.sleep(3)
        print(messages)


asyncio.run(execute())
