from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import rich

# Carregando chave de API

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Funções
# Apenas para formatação de leitura
def cria_linhas(tamanho):
    print("="* tamanho)

cria_linhas(80)

llm = init_chat_model(
    "gemini-2.5-flash",
    model_provider ="google_genai",
    temperature=0.1
)

def classifica_intecao(pergunta):
    system_message = SystemMessage(f"""
        Você é um assistente de inteligência artificial especialista em interpretação,
        contexto e viagens.
        Leia a seguinte pergunta do usuário: {pergunta} e com base no que a
        pergunta pede, defina qual é a intenção dessa pergunta.

        Abaixo, segue a lista de intenções:
            - "guia de viagem",
            - "ideia de local para viajar",
            - "dicas de viagem",
            - "culinaria",
            - "clima",
            - "cultura",
            - "idioma",

        Você deve responder APENAS e SOMENTE a intenção da pergunta do usuário, com base
        na lista de intenções acima.
        Ou seja, se a pergunta do usuário for sobre a criação de um guia de viagem, você
        deve responder:
        "guia de viagem"

        Responda APENAS a intenção do usuário em sua pergunta.
        Qualquer pergunta que seja fora do assunto de viagens ou que possua uma intenção
        diferente, você deve responder:
        "não é sobre viagem"
    """)

    human_message = HumanMessage(pergunta)
    messages = [system_message, human_message]
    llm_intencao_usuario = llm.invoke(messages)
    return str(llm_intencao_usuario.text.strip().lower())

print(classifica_intecao("Quais costumes os brasileiros tem no mes de fevereiro?"))