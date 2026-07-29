from dotenv import load_dotenv
from openai import AsyncOpenAI
import discord
import os


# ============================================================
# 1. Cargar variables del archivo .env
# ============================================================

load_dotenv()

DISCORD_TOKEN = os.getenv("TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


if not DISCORD_TOKEN:
    raise ValueError(
        "No se encontró TOKEN en el archivo .env"
    )

if not ANTHROPIC_API_KEY:
    raise ValueError(
        "No se encontró ANTHROPIC_API_KEY en el archivo .env"
    )


# ============================================================
# 2. Configurar cliente de Claude
# ============================================================

claude_client = AsyncOpenAI(
    api_key=ANTHROPIC_API_KEY,
    base_url="https://api.anthropic.com/v1/",
)


# ============================================================
# 3. Función para consultar a Claude
# ============================================================

async def call_claude(question: str) -> str:
    """Envía una pregunta a Claude y devuelve la respuesta."""

    completion = await claude_client.chat.completions.create(
        model="claude-sonnet-5",
        max_tokens=500,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un asistente útil. "
                    "Responde siempre en español y con estilo de pirata."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    response = completion.choices[0].message.content

    if not response:
        return "Claude no devolvió una respuesta."

    return response


# ============================================================
# 4. Configurar Discord
# ============================================================

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# ============================================================
# 5. Evento de conexión
# ============================================================

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")
    print("El bot está listo para recibir mensajes.")


# ============================================================
# 6. Evento para recibir mensajes
# ============================================================

@client.event
async def on_message(message):

    # Evitar que el bot se responda a sí mismo
    if message.author == client.user:
        return

    message_text = message.content.strip()

    # Comando básico para comprobar Discord
    if message_text.lower() == "$hello":
        await message.channel.send("¡Hola! El bot está conectado.")
        return

    # Comando para realizar una pregunta
    if message_text.lower().startswith("$question"):

        question = message_text[len("$question"):].strip()

        if not question:
            await message.channel.send(
                "Debes escribir una pregunta después de `$question`."
            )
            return

        print(f"Pregunta recibida: {question}")

        try:
            # Mostrar que el bot está escribiendo
            async with message.channel.typing():
                response = await call_claude(question)

            print(f"Respuesta de Claude: {response}")
            print("--------------------------------")

            # Discord permite aproximadamente 2.000 caracteres
            # por mensaje. Se divide la respuesta si es muy larga.
            for position in range(0, len(response), 1900):
                fragment = response[position:position + 1900]
                await message.channel.send(fragment)

        except Exception as error:
            # Mostrar el error real en la terminal
            print("ERROR AL CONSULTAR CLAUDE")
            print(f"Tipo: {type(error).__name__}")
            print(f"Detalle: {error}")

            await message.channel.send(
                "Ocurrió un problema al consultar Claude. "
                "Revisa la terminal de Visual Studio Code."
            )


# ============================================================
# 7. Ejecutar el bot
# ============================================================

client.run(DISCORD_TOKEN)