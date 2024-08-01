from anthropic import Anthropic
import os

def generate_response(prompt, temperature, max_tokens):
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    response = client.completions.create(
        model="claude-2",
        prompt=prompt,
        max_tokens_to_sample=max_tokens,
        temperature=temperature
    )
    
    return response.completion