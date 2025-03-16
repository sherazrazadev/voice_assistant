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
        self._service_context = ServiceContext.from_defaults(
            llm=self._llm, 
            embed_model="local"
        )
        self._index = None
        self._chat_engine = None

        self._create_kb()
        self._create_chat_engine()

    def _create_chat_engine(self):
        # Memory with token limit to maintain context
        memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
        
        # Chat engine with improved prompt and memory
        self._chat_engine = self._index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt=self._prompt,
        )

    def _create_kb(self):
        try:
            reader = SimpleDirectoryReader(
                input_files=[r"/home/ubuntu/voice/VoiceAssistantBot/rag/VoiceAssistant_file.txt"]
            )
            documents = reader.load_data()

            vector_store = QdrantVectorStore(client=self._client, collection_name="VoiceAssistant_db")
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            self._index = VectorStoreIndex.from_documents(
                documents, 
                service_context=self._service_context, 
                storage_context=storage_context
            )
            print("Knowledgebase created successfully!")
        except Exception as e:
            print(f"Error while creating knowledgebase: {e}")

    def interact_with_llm(self, customer_query):
        try:
            # Interact with chat engine and retrieve response
            agent_chat_response = self._chat_engine.chat(customer_query)
            answer = agent_chat_response.response
            # Debugging: Log the raw response
            print(f"Raw LLM Response: {repr(answer)}")
            
            return answer
        except Exception as e:
            print(f"Error during interaction: {e}")

    def get_contextual_response(self, customer_query):
        try:
            # Use memory to provide a contextual response
            agent_chat_response = self._chat_engine.chat(customer_query)
            response = agent_chat_response.response
            return response
        except Exception as e:
            print(f"Error while retrieving contextual response: {e}")
            return "An error occurred while processing your request."

    @property
    def _prompt(self):
        return (
            """
            VoiceAssistant International Chatbot – Emily
            
            Rules:
            - ALWAYS respond with no more than two short sentences.
            - Responses must fit within 10 seconds of speech (approximately 30 words).
            - Use simple, clear language without unnecessary details.
            - Avoid listing multiple strategies or examples unless explicitly asked.
            - For unknown queries, respond: "Sorry, I don’t have that info."
            - Tone should be friendly, professional, and direct.
            
            Example Interactions:
            - Question: "How can I manage my business better?"
              Answer: "Automate repetitive tasks and focus on customer satisfaction."
            - Question: "What tools can I use?"
              Answer: "Use bots for support and lead generation."
            - Question: "What if I don't know the answer?"
              Answer: "Sorry, I don’t have that info."
            """
        )

    def set_llm_parameters(self, temperature=0.3, max_tokens=30):
        # Set LLM parameters for brevity and precision
        self._llm.temperature = temperature
        self._llm.max_tokens = max_tokens

    def set_retrieval_parameters(self, similarity_threshold=0.8):
        # Update Qdrant vector store retrieval settings
        self._service_context.embed_model.set_similarity_threshold(similarity_threshold)
        print("Retrieval parameters updated.")
