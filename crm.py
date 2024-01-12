from aiohttp import ClientResponseError
from fast_bitrix24 import Bitrix
from dataclasses import dataclass

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
            if 'chat' in chat.keys() and chat['chat']['role'] != 'MEMBER' and chat['message'][
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
            self.bitrix.get_all(method='crm.lead.list')
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

    def get_fields_by_deal_id(self):
        response = self.bitrix.call(method='crm.deal.get', items={
            'id': 1
        })
        print(response)


def execute():
    while True:
        webhook_test = 'https://avatarex.bitrix24.ru/rest/42/eg712ozo8h3634fj/'
        bitrix_avatarex = BitrixAvatarex(webhook=webhook_test)
        connection_status: bool = bitrix_avatarex.is_connection_success()
        if not connection_status:
            return
        messages: list[Message] = bitrix_avatarex.get_unanswered_messages()
        for message in messages:
            bitrix_avatarex.send_message(message, gpt.run(message.text))
        # bitrix_avatarex.fill_field()
        # bitrix_avatarex.get_fields_by_deal_id()


execute()
