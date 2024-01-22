import os

from openai import OpenAI
import dotenv

dotenv.load_dotenv()

token = os.getenv('OPENAI')
client = OpenAI(api_key=token)


def test(q):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
    )
    return response


def execute(question: str, thread_id=None, assistant_id='asst_0AE6fTg2tKgNZx0XSK4sj3AU'):
    if thread_id is None:
        thread = client.beta.threads.create()
        thread_id = thread.id

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run.status != 'in_progress':
            break

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    answer = ''
    for message in messages.data[0].content:
        answer += message.text.value + '\n'
    return answer.strip()


#  print(test('test'))