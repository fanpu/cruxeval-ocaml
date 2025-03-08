
def make_translation_prompt(data):
    return f"""You are tasked with translating a Python program to OCaml. Your goal is to create an OCaml program that runs without errors and produces the same output as the original Python code. Follow these steps carefully:

1. First, you will be given a Python program. Analyze it carefully to understand its structure, functionality, and any Python-specific features it uses.

<python_code>
{data["code"]}
print(f({data["input"]}))
</python_code>

2. Before starting the translation, use a <scratchpad> to break down the Python code into its key components and identify any challenging areas for translation. Consider:
   - Data types and structures used
   - Control flow (loops, conditionals)
   - Functions and their parameters
   - Input/output operations
   - Any Python-specific libraries or features

3. Translate the Python code to OCaml, keeping the following guidelines in mind:
   - Maintain the overall structure and logic of the program
   - Use appropriate OCaml data types and structures
   - Implement control flow using OCaml syntax (e.g., `if ... then ... else`, `match ... with`, etc.)
   - Define functions with correct parameters and return types
   - Handle input/output operations using OCaml's standard library functions
   - If the Python code uses list comprehensions or generator expressions, implement them using OCaml's List module functions or recursive functions
   - For any Python libraries used, find equivalent OCaml libraries or implement the functionality from scratch if necessary

4. After translating, review your OCaml code to ensure:
   - All variables are properly declared and initialized
   - Function signatures are correct
   - Pattern matching is used where appropriate
   - Recursion is used effectively where needed
   - The code follows OCaml best practices and idioms

5. Provide your OCaml translation within <ocaml_code> tags.

Remember, the goal is to create a functionally equivalent OCaml program that runs without errors and produces the same output as the original Python code.
"""


def make_translation_prompt_assert(data):
   return f"""You are tasked with translating a Python function to OCaml. Here is the Python function to be translated:

<python_code>
{data["code"]}
assert f({data["input"]}) == {data["output"]}
</python_code>

Your goal is to translate this Python function into OCaml. The OCaml function should be named f, like the Python function. 

When writing the OCaml function, keep the following guidelines in mind:
1. OCaml is a statically-typed language, so you may need to add type annotations.
2. OCaml uses pattern matching extensively, which can often replace if-else statements.
3. OCaml lists are denoted with square brackets and semicolons, e.g., [1; 2; 3].
4. OCaml uses 'let' for variable bindings and 'let rec' for recursive functions.
5. OCaml uses '::' for cons and '@' for list concatenation.

Your translation should be in the following format, ending in a test case where INPUT and OUTPUT should be replaced by the appropriate values from the Python code.
Do NOT include additional test cases or extra testing code, and adhere strictly to the format below.

<ocaml_code>
let f = (* YOUR CODE *)

let () =
  let result = f INPUT in
  let expected_output = EXPECTED_OUTPUT
  assert (result = expected_output);
</ocaml_code>

Please provide the complete OCaml code, including both the translated function and the test case, in your response. Write your entire response inside <ocaml_code>...</ocaml_code> tags.
"""

def parse_translation_result(result):
    if "<ocaml_code>" in result:
        result = result.split("<ocaml_code>")[1]
        if "</ocaml_code>" in result:
            result = result.split("</ocaml_code>")[0]
            return result
    return ""