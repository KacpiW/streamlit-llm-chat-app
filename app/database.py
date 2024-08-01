from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    messages = relationship("ChatMessage", back_populates="chat_history")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    chat_history_id = Column(Integer, ForeignKey("chat_history.id"))
    role = Column(String)
    content = Column(Text)
    chat_history = relationship("ChatHistory", back_populates="messages")

engine = create_engine("sqlite:///chat_history.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def create_new_chat_history(title):
    """Create a new chat history in the database."""
    with Session() as session:
        chat_history = ChatHistory(title=title)
        session.add(chat_history)
        session.commit()
        return chat_history.id

def save_chat_message(chat_history_id, role, content):
    """Save a chat message to the database."""
    with Session() as session:
        message = ChatMessage(chat_history_id=chat_history_id, role=role, content=content)
        session.add(message)
        session.commit()

def load_all_chat_messages(chat_history_id):
    """Load all chat messages from the database."""
    with Session() as session:
        messages = session.query(ChatMessage).filter(ChatMessage.chat_history_id == chat_history_id).all()
        return messages

def get_last_chat_message(current_chat_id):
    """Get the last chat message from the database."""
    with Session() as session:
        last_message = session.query(ChatMessage).filter(ChatMessage.chat_history_id == current_chat_id).order_by(ChatMessage.id.desc()).first()
        return last_message

def load_all_chat_histories():
    with Session() as session:
        chat_histories = session.query(ChatHistory).all()
        return chat_histories