# Import the chat requirements
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# Global store for chat histories
# Consider replacing this with a more persistent storage solution for production use
chat_histories_store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    # Retrieve or initialize chat history for a session.
    global chat_histories_store
    if session_id not in chat_histories_store:
        chat_histories_store[session_id] = ChatMessageHistory()
    return chat_histories_store[session_id]

# Initialize and load your LLM, RAG DB, and conversational memory here
def setup_llm_and_db(retriever):

  # Define the LLM to be used - comment out to change models
  chat = ChatOpenAI(
    temperature=0,
    model_name="gpt-3.5-turbo"
  )
  # Define the LLM to be used - comment out to change models
#   chat = ChatAnthropic(
#     temperature=0,
#     model_name="claude-3-sonnet-20240229"
# )

  # Institute chat and question summarization for retrieval
  ### Contextualize question ###
  contextualize_q_system_prompt = """
  Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Match the language of the question or chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is.
  """

  contextualize_q_prompt = ChatPromptTemplate.from_messages(
      [
          ("system", contextualize_q_system_prompt),
          MessagesPlaceholder("chat_history"),
          ("human", "{input}"),
      ]
  )
  history_aware_retriever = create_history_aware_retriever(
      chat, retriever, contextualize_q_prompt
  )

  # Define the custom prompt template - here is where prompt engineering might improve answers
  _DEFAULT_TEMPLATE = """
You are a senior developer with extensive expertise in the ApostropheCMS ecosystem (version 3 and above). Your main responsibility is to find and provide links to documents that answer users' questions about developing within the ApostropheCMS framework. Utilize the RAG database documents provided in the context below to inform your answers. When crafting answers, please adhere to the guidelines below and return the response in markdown format with all links opening in a new window:

1. Relevance to ApostropheCMS Development: Only respond to inquiries that pertain to developing for ApostropheCMS. If a question falls outside this domain, kindly inform the user that it is beyond the scope of your expertise. However, consider whether reformulating the question to align with ApostropheCMS development is possible. For example, if a user asks "How can I set my computer up?" you could respond to the question "How can I set my computer up for developing with ApostropheCMS?".
2. Provide Link(s) to the Document(s): LINKS SHOULD OPEN IN A NEW WINDOW - in order to do this return all links as plain HTML, not markdown with the form `<a src="URL" target="_blank">PAGE_TITLE</a>`. Your primary duty when answering a question is to provide the top 2-3 unique links to the relevant document(s) in the ApostropheCMS documentation. This link URL can be copied directly from the URL added to the RAG database document. If no document exists, inform the user that the information is not available in the documentation.
3. Provide a Brief Summary: Provide a brief summary of the document(s) (no more than 2 sentences) and how they match the user's question.
The answer should start with the links followed by the summary.
At the end of your answer add a newline followed by this content:
"I hope this information helps! If you have any further questions, please don't hesitate to ask. For more technical help please join our Discord server at https://discord.com/invite/HwntQpADJr."
Furthermore, enable users to request responses in languages other than English to accommodate a broader audience. If the user asks a question in a language other than English, respond automatically in that language. This feature enhances the accessibility and usability of your support.

Context:
{context}
"""

  qa_prompt = ChatPromptTemplate.from_messages(
      [
          ("system", _DEFAULT_TEMPLATE),
          MessagesPlaceholder("chat_history"),
          ("human", "{input}"),
      ]
  )
  
  document_prompt = PromptTemplate(
      template="{page_content}{url}",
      input_variables=["page_content", "url"]
  )

  question_answer_chain = create_stuff_documents_chain(llm=chat, prompt=qa_prompt, document_prompt=document_prompt)

  rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

  conversational_rag_chain = RunnableWithMessageHistory(
      rag_chain,
      get_session_history,
      input_messages_key="input",
      history_messages_key="chat_history",
      output_messages_key="answer",
  )

  return conversational_rag_chain


def get_response(user_question, retriever, session_id="default_session"):
  conversational_rag_chain = setup_llm_and_db(retriever)

  # Function invocation with the user's question and configuration
  response = conversational_rag_chain.invoke(
      {"input": user_question},
      config={
          "configurable": {"session_id": session_id}
      }
  )

  # Extracting the answer from the response
  answer = response["answer"]

  return answer

