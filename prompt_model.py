# o3-mini-2025-01-31

from openai import OpenAI
import time
import os
from diskcache import Cache
import random

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def generate_content(o3_assistant_prompt: str, o3_user_prompt: str) -> str:
    prompt = f"{o3_assistant_prompt}\nUser request: {o3_user_prompt}"
    messages = [
        {"role": "assistant", "content": o3_assistant_prompt},
        {"role": "user", "content": o3_user_prompt}
    ]
    response = client.chat.completions.create(
        model="o3-mini",
        messages=messages,
        reasoning_effort="high"  # This can be set to low, medium or high.
    )
    return response.choices[0].message.content

def apply_openai_api_fast(text, system_prompt = None, max_retries=5, initial_delay=5, n_samples=1, max_tokens=500, ignore_cache=False, replace_cache=False, cache_name='cache_diskcache', temperature=0.5):
    model = "o3-mini-2025-01-31"
    if system_prompt == None:
        system_prompt = "You are an expert at coding in Python and OCaml."

    with Cache(cache_name) as db:
        key = system_prompt + text + str(temperature) + model
        samples_to_generate = n_samples
        if not ignore_cache and key in db and len(db[key]) >= n_samples:
            result = db[key]
            return random.sample(result, n_samples)
        if not ignore_cache and key in db:
            samples_to_generate -= len(db[key])
        
        samples = []
        retries = 0
        while len(samples) < samples_to_generate and retries < max_retries:
            try:
                messages = [
                    {"role": "assistant", "content": system_prompt},
                    {"role": "user", "content": text}
                ]
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    reasoning_effort="low"  # This can be set to low, medium or high.
                )
                response = response.choices[0].message.content
                samples.append(response)
                print("got a response!")
                # db[key] = bytes(response, "utf-8")
                if key in db and not replace_cache:
                    db[key] = db[key] + [response]
                else:
                    db[key] = [response]
            except Exception as e:
                if e.status_code == 429:  # Rate limit error
                    if retries < max_retries - 1:
                        # delay = initial_delay * (2 ** attempt)  # Exponential backoff
                        delay = initial_delay + retries
                        print(f"Rate limit hit. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print(f"Max retries reached. Could not process: {text}")
                        return f"Error: Rate limit exceeded after {max_retries} attempts"
                else:
                    print(f"API error occurred: {e}")
                    return f"Error: {str(e)}"
        return db[key]

