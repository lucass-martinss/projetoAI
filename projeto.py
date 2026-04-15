from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

# =========================
# Carregando variáveis
# =========================
load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY não encontrada no ambiente.")

# =========================
# Apenas para formatação
# =========================
def cria_linhas(tamanho=80):
    print("=" * tamanho)

cria_linhas()

# =========================
# Inicializando o modelo
# =========================
llm = init_chat_model(
    "gemini-2.5-flash",
    model_provider="google_genai",
    temperature=0.1
)

# =========================
# Base simples de estoque
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
        "harmonizacao": "entradas, saladas, comidas leves, cozinha mediterrânea"
    },
    "espumante": {
        "disponivel": True,
        "quantidade": 9,
        "tipos": ["brut", "moscatel", "nature"],
        "temperatura": "entre 6°C e 8°C",
        "harmonizacao": "aperitivos, sobremesas, frutos do mar, comemorações"
    },
    "vinho suave": {
        "disponivel": False,
        "quantidade": 0,
        "tipos": ["tinto suave", "branco suave"],
        "temperatura": "entre 10°C e 14°C",
        "harmonizacao": "sobremesas, queijos leves, consumo casual"
    }
}

INTENCOES_VALIDAS = {
    "orientação de consumo",
    "disponibilidade de vinho",
    "harmonização",
    "temperatura de serviço",
    "recomendação de vinho",
    "tipos de vinho",
    "não é sobre vinhos"
}

# =========================
# Classificador de intenção
# =========================
def classifica_intencao(pergunta):
    system_message = SystemMessage("""
Você é um assistente virtual de SAC de uma adega de vinhos.

Seu trabalho é analisar a pergunta do cliente e responder APENAS com uma das intenções abaixo:

- orientação de consumo
- disponibilidade de vinho
- harmonização
- temperatura de serviço
- recomendação de vinho
- tipos de vinho

Se a pergunta não for sobre vinhos, adega, consumo, harmonização, recomendação ou disponibilidade,
responda exatamente:
não é sobre vinhos

Responda somente com a intenção, sem explicações.
""")

    human_message = HumanMessage(pergunta)
    resposta = llm.invoke([system_message, human_message]).content.strip().lower()

    if resposta not in INTENCOES_VALIDAS:
        return "não é sobre vinhos"
    return resposta

# =========================
# Busca no estoque
# =========================
def busca_vinho_na_pergunta(pergunta):
    pergunta = pergunta.lower()
    for vinho in estoque_vinhos.keys():
        if vinho in pergunta:
            return vinho

        for tipo in estoque_vinhos[vinho]["tipos"]:
            if tipo in pergunta:
                return vinho

    return None

# =========================
# Respostas do SAC
# =========================
def responder_cliente(pergunta):
    intencao = classifica_intencao(pergunta)
    vinho_encontrado = busca_vinho_na_pergunta(pergunta)

    if intencao == "não é sobre vinhos":
        return "Desculpe, eu só posso ajudar com informações sobre vinhos, consumo, harmonização e disponibilidade da adega."

    if intencao == "disponibilidade de vinho":
        if vinho_encontrado:
            dados = estoque_vinhos[vinho_encontrado]
            if dados["disponivel"]:
                return (
                    f"Temos {vinho_encontrado} disponível em estoque.\n"
                    f"Quantidade atual: {dados['quantidade']} unidades.\n"
                    f"Tipos disponíveis: {', '.join(dados['tipos'])}."
                )
            else:
                return f"No momento, o {vinho_encontrado} está indisponível em nosso estoque."
        else:
            return "Por favor, informe qual tipo de vinho deseja consultar: vinho tinto, branco, rosé, espumante ou suave."

    if intencao == "harmonização":
        if vinho_encontrado:
            dados = estoque_vinhos[vinho_encontrado]
            return f"O {vinho_encontrado} harmoniza bem com: {dados['harmonizacao']}."
        else:
            return "Informe o tipo de vinho para eu sugerir a melhor harmonização."

    if intencao == "temperatura de serviço":
        if vinho_encontrado:
            dados = estoque_vinhos[vinho_encontrado]
            return f"A temperatura ideal para servir {vinho_encontrado} é {dados['temperatura']}."
        else:
            return "Informe o tipo de vinho para eu dizer a temperatura ideal de serviço."

    if intencao == "tipos de vinho":
        resposta = ["Temos os seguintes tipos de vinho cadastrados na adega:"]
        for vinho, dados in estoque_vinhos.items():
            resposta.append(f"- {vinho.title()}: {', '.join(dados['tipos'])}")
        return "\n".join(resposta)

    if intencao == "orientação de consumo":
        return (
            "Para orientar o consumo corretamente, eu posso ajudar com:\n"
            "- tipo de vinho ideal para a ocasião;\n"
            "- temperatura de serviço;\n"
            "- harmonização com alimentos;\n"
            "- intensidade e perfil do vinho.\n"
            "Se quiser, me diga o prato, ocasião ou tipo de vinho desejado."
        )

    if intencao == "recomendação de vinho":
        system_message = SystemMessage("""
Você é um sommelier virtual de uma adega de vinhos.
Com base na pergunta do cliente, recomende vinhos de forma objetiva e amigável.
Considere ocasião, prato, preferência por vinho seco/suave, tinto/branco/rosé/espumante.
Responda em português do Brasil.
""")
        human_message = HumanMessage(
            f"Pergunta do cliente: {pergunta}\n\n"
            f"Estoque disponível: {estoque_vinhos}"
        )
        return llm.invoke([system_message, human_message]).content.strip()

    return "Não consegui identificar a necessidade do cliente com clareza."

# =========================
# Teste
# =========================
if __name__ == "__main__":
    cria_linhas()
    pergunta = "Vocês têm vinho tinto disponível? Qual combina com churrasco?"
    print(f"Pergunta do cliente: {pergunta}")
    cria_linhas()
    print("Intenção identificada:", classifica_intencao(pergunta))
    cria_linhas()
    print("Resposta do SAC:")
    print(responder_cliente(pergunta))
    cria_linhas()
