from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
import os

# =========================
# Carregando variáveis
# =========================
load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY não encontrada no ambiente.")

# =========================
# Utilitário visual
# =========================
def cria_linhas(tamanho=80):
    print("=" * tamanho)

# =========================
# Inicializando modelo
# =========================
llm = init_chat_model(
    "gemini-2.5-flash",
    model_provider="google_genai",
    temperature=0.1
)

# =========================
# Estoque mockado
# =========================
estoque_vinhos = {
    "vinho tinto": {
        "disponivel": True,
        "quantidade": 18,
        "tipos": ["cabernet sauvignon", "merlot", "malbec", "pinot noir"],
        "temperatura": "entre 14°C e 18°C",
        "harmonizacao": "carnes vermelhas, massas com molho forte, queijos curados"
    },
    "vinho branco": {
        "disponivel": True,
        "quantidade": 12,
        "tipos": ["chardonnay", "sauvignon blanc", "riesling"],
        "temperatura": "entre 8°C e 12°C",
        "harmonizacao": "peixes, frutos do mar, saladas, queijos leves"
    },
    "vinho rosé": {
        "disponivel": True,
        "quantidade": 7,
        "tipos": ["rosé seco", "rosé suave"],
        "temperatura": "entre 8°C e 12°C",
        "harmonizacao": "entradas, saladas, comidas leves"
    },
    "espumante": {
        "disponivel": True,
        "quantidade": 9,
        "tipos": ["brut", "moscatel", "nature"],
        "temperatura": "entre 6°C e 8°C",
        "harmonizacao": "aperitivos, sobremesas, frutos do mar"
    },
    "vinho suave": {
        "disponivel": False,
        "quantidade": 0,
        "tipos": ["tinto suave", "branco suave"],
        "temperatura": "entre 10°C e 14°C",
        "harmonizacao": "sobremesas, queijos leves"
    }
}

# =========================
# Classificação de intenção
# =========================
INTENCOES_VALIDAS = {
    "orientação de consumo",
    "disponibilidade de vinho",
    "harmonização",
    "temperatura de serviço",
    "recomendação de vinho",
    "tipos de vinho",
    "não é sobre vinhos"
}

def classifica_intencao(pergunta: str) -> str:
    system_message = SystemMessage("""
Você é um assistente virtual de SAC de uma adega de vinhos.

Classifique a intenção da pergunta do cliente usando APENAS uma das opções:
- orientação de consumo
- disponibilidade de vinho
- harmonização
- temperatura de serviço
- recomendação de vinho
- tipos de vinho

Se a pergunta não for sobre vinhos, adega, consumo, harmonização, recomendação ou disponibilidade,
responda exatamente:
não é sobre vinhos

Responda somente com a intenção.
""")

    human_message = HumanMessage(pergunta)
    resposta = llm.invoke([system_message, human_message]).content.strip().lower()

    if resposta not in INTENCOES_VALIDAS:
        return "não é sobre vinhos"
    return resposta

# =========================
# Busca de vinho citado
# =========================
def busca_vinho_na_pergunta(pergunta: str):
    pergunta = pergunta.lower()
    for vinho, dados in estoque_vinhos.items():
        if vinho in pergunta:
            return vinho
        for tipo in dados["tipos"]:
            if tipo in pergunta:
                return vinho
    return None

# =========================
# Resposta híbrida
# =========================
def responder_cliente(pergunta: str, historico: list) -> str:
    intencao = classifica_intencao(pergunta)
    vinho_encontrado = busca_vinho_na_pergunta(pergunta)

    if intencao == "não é sobre vinhos":
        return "Desculpe, eu só posso ajudar com vinhos, harmonização, consumo e disponibilidade."

    if intencao == "disponibilidade de vinho":
        if vinho_encontrado:
            dados = estoque_vinhos[vinho_encontrado]
            if dados["disponivel"]:
                return (
                    f"Temos {vinho_encontrado} disponível no momento. "
                    f"Quantidade atual: {dados['quantidade']} unidades. "
                    f"Tipos disponíveis: {', '.join(dados['tipos'])}."
                )
            return f"No momento, o {vinho_encontrado} está indisponível em nosso estoque."
        return "Claro. Me diga qual vinho você quer consultar: tinto, branco, rosé, espumante ou suave."

    if intencao == "harmonização":
        if vinho_encontrado:
            dados = estoque_vinhos[vinho_encontrado]
            return f"O {vinho_encontrado} harmoniza bem com {dados['harmonizacao']}."
        return "Me diga o tipo de vinho ou o prato que você vai servir, e eu sugiro a harmonização."

    if intencao == "temperatura de serviço":
        if vinho_encontrado:
            dados = estoque_vinhos[vinho_encontrado]
            return f"A temperatura ideal para servir {vinho_encontrado} é {dados['temperatura']}."
        return "Me diga qual vinho você quer servir para eu informar a temperatura ideal."

    if intencao == "tipos de vinho":
        resposta = ["Temos estes tipos de vinho disponíveis na adega:"]
        for vinho, dados in estoque_vinhos.items():
            resposta.append(f"- {vinho.title()}: {', '.join(dados['tipos'])}")
        return "\n".join(resposta)

    if intencao == "orientação de consumo":
        return (
            "Posso te orientar sobre tipo de vinho, temperatura de serviço, harmonização e ocasião ideal. "
            "Me diga o prato, a ocasião ou sua preferência."
        )

    if intencao == "recomendação de vinho":
        system_message = SystemMessage("""
Você é um atendente virtual de uma adega de vinhos.
Responda de forma natural, simpática e objetiva em português do Brasil.

Use o histórico da conversa para manter contexto.
Considere:
- ocasião
- prato
- preferência por vinho tinto, branco, rosé ou espumante
- preferência por seco ou suave
- disponibilidade em estoque

Se recomendar um vinho, priorize os que estão disponíveis no estoque informado.
""")

        contexto_estoque = f"Estoque atual: {estoque_vinhos}"

        mensagens = [system_message]
        mensagens.append(SystemMessage(contexto_estoque))
        mensagens.extend(historico)
        mensagens.append(HumanMessage(pergunta))

        resposta = llm.invoke(mensagens).content.strip()
        return resposta

    return "Não consegui entender totalmente sua solicitação. Pode reformular?"

# =========================
# Chat no console
# =========================
def iniciar_chat():
    historico = []

    cria_linhas()
    print("SAC da Adega Virtual iniciado.")
    print("Digite sua pergunta.")
    print("Para encerrar, digite: sair")
    cria_linhas()

    while True:
        pergunta = input("Cliente: ").strip()

        if not pergunta:
            print("Atendente: Por favor, digite uma pergunta.")
            continue

        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("Atendente: Obrigado pelo contato. Até logo!")
            break

        resposta = responder_cliente(pergunta, historico)

        print(f"Atendente: {resposta}")
        cria_linhas()

        historico.append(HumanMessage(pergunta))
        historico.append(AIMessage(resposta))

# =========================
# Execução
# =========================
if __name__ == "__main__":
    iniciar_chat()
