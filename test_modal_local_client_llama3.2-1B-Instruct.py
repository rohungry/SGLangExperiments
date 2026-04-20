from openai import OpenAI

client = OpenAI(
    base_url="<your modal servername here>" # mine was: https://rohunkshirsagar--llama-sglang-test-serve.modal.run/v1",
    api_key="not-needed",  # SGLang doesn't check, but the client requires a value
)
messages = []

while True:
    user = input("you: ")
    if not user:
        break
    messages.append({"role": "user", "content": user})
    resp = client.chat.completions.create(
        model="meta-llama/Llama-3.2-1B-Instruct",
        messages=messages,
        temperature=0.2,
        max_tokens=200,
    )
    reply = resp.choices[0].message.content
    print(f"assistant: {reply}\n")
    messages.append({"role": "assistant", "content": reply})