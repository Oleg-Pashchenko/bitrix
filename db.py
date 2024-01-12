from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
import dotenv
import os

Base = declarative_base()


class Chats(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    thread_id = Column(Integer, nullable=False)
    account_id = Column(Integer, nullable=False)


class Accounts(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    api_key = Column(String, nullable=False)
    assistant_id = Column(String, nullable=False)
    pipeline_id = Column(String, nullable=False)
    stages = Column(JSON)
    bitrix_webhook = Column(String)


# Function to get all accounts
def get_all_accounts(session):
    return session.query(Accounts).all()


# Function to get thread_id by chat_id or return None if not found
def get_thread_id_by_chat_id(session, chat_id):
    chat = session.query(Chats).filter_by(chat_id=chat_id).first()
    return chat.thread_id if chat else None


# Example Usage
if __name__ == "__main__":

    dotenv.load_dotenv()
    # Replace 'postgresql://username:password@localhost/dbname' with your actual PostgreSQL connection string
    engine = create_engine(f'postgresql://'
                           f'{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@'
                           f'{os.getenv("DB_HOST")}:5432/{os.getenv("DB_NAME")}')

    # Create table
    Base.metadata.create_all(engine)

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Example: Inserting data
    chat = Chats(chat_id=1, thread_id=101)
    account = Accounts(api_key='your_api_key', assistant_id='your_assistant_id', pipeline_id='your_pipeline_id',
                       stages={'stage': 'value'}, bitrix_webhook='your_webhook')

    session.add(account)
    session.commit()

    # Example: Retrieving data
    all_accounts = get_all_accounts(session)
    print("All Accounts:")
    for acc in all_accounts:
        print(acc.api_key, acc.assistant_id, acc.pipeline_id)

    chat_id_to_search = 1
    thread_id = get_thread_id_by_chat_id(session, chat_id_to_search)
    print(f"Thread ID for Chat ID {chat_id_to_search}: {thread_id}")

    # Close the session
    session.close()

