import random
import zlib
import json
import dbm
import anthropic
import time
from diskcache import Cache

import os
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

def apply_anthropic_api_fast(text, system_prompt = None, max_retries=5, initial_delay=5, n_samples=1, max_tokens=500, ignore_cache=False, replace_cache=False, cache_name='cache_diskcache', temperature=0.5):
    if system_prompt == None:
        system_prompt = "You are an expert at coding in Python and OCaml."

    with Cache(cache_name) as db:
        key = system_prompt + text + str(temperature)
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
                message = client.messages.create(
                    # model="claude-3-5-sonnet-20240620",
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": text
                                }
                            ]
                        }
                    ]
                )
                response = message.content[0].text
                samples.append(response)
                print("got a response!")
                # db[key] = bytes(response, "utf-8")
                if key in db and not replace_cache:
                    db[key] = db[key] + [response]
                else:
                    db[key] = [response]
            except anthropic.APIStatusError as e:
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
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return f"Error: {str(e)}"
        return db[key]

from prompts import (
    make_translation_prompt, 
    make_translation_prompt_assert,
    parse_translation_result,
)
from prompt_model import apply_openai_api_fast

def prompt_translation(data):
    prompt = make_translation_prompt_assert(data)
    # result = apply_anthropic_api_fast(prompt, None, max_retries=1000, initial_delay=5, max_tokens=5000)
    result = apply_openai_api_fast(prompt, None, max_retries=1000, initial_delay=5, max_tokens=5000)
    result = parse_translation_result(result[0])
    return result

from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

def parallel_prompt_translation(all_data, max_workers=None):
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(prompt_translation, data) for data in all_data]
        
        results = []
        with tqdm(total=len(futures), desc="Processing queries") as pbar:
            for i, future in enumerate(futures):
                try: results.append(future.result())
                except Exception as e: print(e); print("error!", i)
                finally: pbar.update(1)
    return results



from datasets import load_dataset

ds = load_dataset("cruxeval-org/cruxeval")["test"]
# res = make_translation_prompt(ds[0])
res = parallel_prompt_translation([ds[i] for i in range(0, 100)])

from utils import remove_ocaml_comments
res = [remove_ocaml_comments(r) for r in res]


# def make_code(data):
#     return f"""{data['code']}
# print(f({data['input']}))"""

from run import parallel_run_ocaml
results = parallel_run_ocaml(res)

def extract_ocaml_output(translation):
    if "assert (result = " in translation:
        translation = translation.split("assert (result = ")[1]
        if ")" in translation:
            return translation.split(")")[0]
    return "ERROR"

correct = 0
data = []

for i, (output, error) in enumerate(results):
    if error != None:
        print(ds[i]["code"])
        print(f"assert f({ds[i]['input']}) == {ds[i]['output']}")
        print("***")
        print(res[i].strip())
        print(output)
        print("-"*100)
        continue
    
    ocaml_output = extract_ocaml_output(res[i].strip())
    data.append({
        "ocaml_code": res[i].strip(),
        "output": ocaml_output, 
        "python_input": ds[i]["input"],
        "python_output": ds[i]["output"],
        "python_code": ds[i]["code"],
    })
    correct += 1
    # print(ds[i]["code"])
    # print("***")
    # print(res[i].strip())
    # print(output)
    # print("-"*100)

print(correct)


# def eq(py_output, ocaml_output):
#     if py_output.startswith("'") and py_output.endswith("'"):
#         return py_output[1:-1] == ocaml_output
#     elif ocaml_output.startswith("[") and ocaml_output.endswith("]"):
#         return py_output == ocaml_output.replace("; ", ", ")
#     else:
#         return py_output == ocaml_output
    
# correct = 0
# data = []
# for i, (output, error) in enumerate(results):
#     if output == None: continue
#     py_output = ds[i]["output"]
#     ocaml_output = output[:-1]
#     if eq(py_output, ocaml_output):
#         data.append({
#             "ocaml_code": res[i].strip(),
#             "output": ocaml_output, 
#             "python_input": ds[i]["input"],
#             "python_output": ds[i]["output"],
#             "python_code": ds[i]["code"],
#         })
#         correct += 1
#     else:
#         print(f"[{py_output}][{ocaml_output}]")
#         print(py_output, ocaml_output, eq(py_output, ocaml_output))
#         print("[PYTHON]")
#         print(ds[i]["code"])
#         print("[OCAML]")
#         print(res[i].strip())
#         print("-"*100)

# print(correct)

# for d in data:
#     print(d)

from datasets import Dataset
dataset = Dataset.from_list(data)
dataset.push_to_hub("minimario/cruxeval-ocaml")

# # for i in range(5):
# #     print(make_code(ds[i]))
# #     print("\n")
# #     print(res[i])
# #     print("-"*100)