from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()                      # reads your key from the .env file
client = Anthropic()               # connects to the model using that key

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
)

print(response.content[0].text)    # print the model's reply
