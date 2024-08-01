import openai
import os

def generate_response(prompt, temperature, max_tokens):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Adjust the model as needed
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return response.choices[0].message['content']