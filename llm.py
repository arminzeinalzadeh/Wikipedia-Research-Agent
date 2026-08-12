import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()
OpenRouter_API = os.getenv("OpenRouter_API")


model = "openai/gpt-oss-120b:free"

model = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OpenRouter_API,
    model=model,
    temperature=0,
)

if __name__ == "__main__":
    response = model.invoke("hello")
    print("test message")
    print(response.content)


