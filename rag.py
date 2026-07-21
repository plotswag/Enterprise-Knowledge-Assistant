import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

from langchain_core.messages import HumanMessage, AIMessage


# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env file")


# ==========================================================
# Greeting Keywords
# ==========================================================

GREETINGS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "hola",
    "yo"
}

THANKS = {
    "thanks",
    "thank you",
    "thx",
    "thanks a lot"
}

GOODBYE = {
    "bye",
    "goodbye",
    "see you",
    "see ya",
    "take care"
}

SMALL_TALK = {
    "how are you",
    "who are you",
    "what can you do",
    "help",
    "can you help me",
    "what is your name"
}


# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VECTOR_DB_PATH = os.path.join(
    BASE_DIR,
    "vector_db"
)


# ==========================================================
# Embedding Model
# ==========================================================

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)


# ==========================================================
# Load FAISS Vector Database
# ==========================================================

vector_db = FAISS.load_local(
    folder_path=VECTOR_DB_PATH,
    embeddings=embeddings,
    index_name="technova_faiss",
    allow_dangerous_deserialization=True
)

print("✅ Vector DB Loaded Successfully")
print(f"📄 Total Chunks : {vector_db.index.ntotal}")


# ==========================================================
# Retriever
# ==========================================================

retriever = vector_db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,
        "lambda_mult": 0.7
    }
)


# ==========================================================
# Large Language Model
# ==========================================================

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=GROQ_API_KEY
)
# ==========================================================
# Prompt Template
# ==========================================================

prompt = ChatPromptTemplate.from_template("""
You are an Enterprise Knowledge Assistant.

Your job is to answer questions ONLY using the retrieved company documents.

Rules:

1. Answer only from the provided context.
2. If multiple documents contain relevant information, combine them into one answer.
3. Do not make up policies or information.
4. If the answer cannot be found in the context, reply exactly:

"I couldn't find that information in the available company documents."

5. Keep your answer professional, clear, and concise.

==========================
Context:
{context}
==========================

Question:
{input}

Answer:
""")


# ==========================================================
# Create LangChain Chains
# ==========================================================

document_chain = create_stuff_documents_chain(
    llm,
    prompt
)

retrieval_chain = create_retrieval_chain(
    retriever,
    document_chain
)


# ==========================================================
# Conversation Memory
# ==========================================================

chat_history = []


# ==========================================================
# Ask Question Function
# ==========================================================

def ask_question(question: str):

    global chat_history

    q = question.lower().strip()

    # =====================================
    # Greeting
    # =====================================

    if any(greeting == q for greeting in GREETINGS):

        return {
            "answer":
                "👋 Hello! Welcome to the Enterprise Knowledge Assistant.\n\n"
                "I can help you with:\n"
                "• HR Policies\n"
                "• Leave Policies\n"
                "• Employee Benefits\n"
                "• IT Guidelines\n"
                "• Company Rules\n"
                "• Internal Documents\n\n"
                "How can I assist you today?",
            "sources": []
        }

    # =====================================
    # Thanks
    # =====================================

    if any(word == q for word in THANKS):

        return {
            "answer":
                "😊 You're welcome! Feel free to ask me anything about your company documents.",
            "sources": []
        }

    # =====================================
    # Goodbye
    # =====================================

    if any(word == q for word in GOODBYE):

        return {
            "answer":
                "👋 Goodbye! Have a wonderful day.",
            "sources": []
        }

    # =====================================
    # Small Talk
    # =====================================

    if any(word == q for word in SMALL_TALK):

        response = llm.invoke(
            f"""
You are a friendly AI assistant.

Reply naturally to the following message.

User:
{question}

Keep the answer under 60 words.
"""
        )

        return {
            "answer": response.content,
            "sources": []
        }

    # =====================================
    # Retrieve Documents
    # =====================================

    result = retrieval_chain.invoke(
        {
            "input": question,
            "chat_history": chat_history
        }
    )

    answer = result.get("answer", "")
    # =====================================
    # Save Chat History
    # =====================================

    chat_history.append(
        HumanMessage(content=question)
    )

    chat_history.append(
        AIMessage(content=answer)
    )

    # =====================================
    # Extract Sources
    # =====================================

    sources = []

    for doc in result.get("context", []):

        metadata = doc.metadata or {}

        source = {
            "file": os.path.basename(
                metadata.get("source", "Unknown")
            ),
            "page": metadata.get("page", "-")
        }

        # Prevent duplicate entries
        if source not in sources:
            sources.append(source)

    # =====================================
    # Return Response
    # =====================================

    return {
        "answer": answer,
        "sources": sources
    }


# ==========================================================
# Clear Chat Function
# ==========================================================

def clear_chat():

    global chat_history

    chat_history.clear()


# ==========================================================
# Test (Only when running rag.py directly)
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("Enterprise Knowledge Assistant")
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:

        question = input("\nYou: ")

        if question.lower() in ["exit", "quit"]:
            break

        response = ask_question(question)

        print("\nAssistant:")
        print(response["answer"])

        if response["sources"]:

            print("\nSources:")

            for source in response["sources"]:

                print(
                    f"- {source['file']} "
                    f"(Page: {source['page']})"
                )
                    