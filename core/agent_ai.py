from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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",
)

while True:
    mensaje = input("Que deseas preguntar? \n")
    if mensaje.lower() == "salir":
        break

    completion = client.chat.completions.create(
        model="minimaxai/minimax-m2.7",
        messages=[{"role": "user", "content": mensaje}],
        temperature=1,
        top_p=0.95,
        max_tokens=8192,
        stream=False,
    )

    print(completion.choices[0].message.content)
