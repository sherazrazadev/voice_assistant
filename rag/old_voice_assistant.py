from qdrant_client import QdrantClient
from llama_index.llms.ollama import Ollama
from llama_index.core import SimpleDirectoryReader
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import ServiceContext, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage.storage_context import StorageContext

import warnings
warnings.filterwarnings("ignore")

class AIVoiceAssistant:
    def __init__(self):
        self._qdrant_url = "http://localhost:6333"
        self._client = QdrantClient(url=self._qdrant_url, prefer_grpc=False)
        self._llm = Ollama(model="llama3.2:1b", request_timeout=120.0)
        self._service_context = ServiceContext.from_defaults(llm=self._llm, embed_model="local")
        self._index = None
        self._chat_engine = None

        self._create_kb()
        self._create_chat_engine()

    def _create_chat_engine(self):
        memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
        self._chat_engine = self._index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt=self._prompt,
        )
    
    
    def _create_kb(self):
        try:
                    # Check if "Botmer_db" collection already exists
            # collections = self._client.get_collections().collections
            # if any(collection.name == "Botmer_db" for collection in collections):
            #     print("Knowledgebase already exists. Skipping creation.")
            
            reader = SimpleDirectoryReader(
                input_files=[r"/home/ubuntu/voice/VoiceAssistantBot/rag/botmer_file.txt"]
            )
            documents = reader.load_data()
            vector_store = QdrantVectorStore(client=self._client, collection_name="Botmer_db")
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            self._index = VectorStoreIndex.from_documents(
                documents, service_context=self._service_context, storage_context=storage_context
            )
            print("Knowledgebase created successfully!")
        except Exception as e:
            print(f"Error while creating knowledgebase: {e}")
    




    def interact_with_llm(self, customer_query):
        AgentChatResponse = self._chat_engine.chat(customer_query)
        answer = AgentChatResponse.response
        return answer

    @property
    def _prompt(self):
        return  """
                Botmer International Chatbot – Emily
                  Greeting:
                  "Hello! This is Emily from Botmer International. How can I help?"
                  Interaction Flow:
                  1. Customer Inquiry:
                  "How can I assist you?"
                  2. Response Guidelines:
                  - Responses must fit within 10 seconds of speech.
                  - Limit each response to a maximum of 2 short sentences.
                  - No unnecessary elaboration, examples, or details.
                  - Use simple, clear language.
                  - Avoid abbreviations or complex phrasing.
                  3. Unknown Query:
                  - "Sorry, I don’t have that info."
                  4. Tone:
                  - Friendly, professional, and direct.
                  - Focus strictly on service-related queries.
                  Closing:
                  "Thank you! Have a great day."
                  Example Interactions:
                  - Greeting:
                  "Hello! This is Emily from Botmer International. How can I help?"
                  - Customer Inquiry:
                  "How can I assist you?"
                  - Unknown Query:
                  "Sorry, I don’t have that info."
                  - Closing:
                  "Thank you! Have a great day."
                """


