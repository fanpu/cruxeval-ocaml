import subprocess
import tempfile
from diskcache import Cache
import json
import os
from concurrent.futures import ProcessPoolExecutor

dir = "/home/minimario/Documents/cruxeval-ocaml/tmp"

def run_ocaml(code_snippet, cache_name='ocaml_cache'):
    with Cache(cache_name) as db:
        key = code_snippet
        if key in db:
            result = json.loads(db[key].decode("utf-8"))
            return result[0], result[1]
        
        # Create a temporary file with the code snippet
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ml', delete=False, dir=dir) as temp_file:
            temp_file.write(code_snippet)
            temp_filename = temp_file.name[len(dir)+1:]

        try:
            # Run the Lean compiler on the temporary file
            result = subprocess.run(
                ['ocaml', temp_filename],
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                timeout=2,
                cwd=dir,
            )
            output = result.stdout
            error = None
        except subprocess.CalledProcessError as e:
            output = None
            error = e.stderr
        except Exception as e:
            output = None
            error = str(e)
        finally:
            os.unlink(os.path.join(dir, temp_filename))

        # result = (syntax_valid, error_message)
        # db[key] = bytes(json.dumps(result), "utf-8")
    
        return output, error

def parallel_run_ocaml(queries, max_workers=None) -> tuple[bool, str]:
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_ocaml, query) for query in queries]
        results = [future.result() for future in futures]
    return results

code = """(* Helper function to count occurrences of an element in a list *)
let count x lst =
  List.fold_left (fun acc elem -> if elem = x then acc + 1 else acc) 0 lst

(* Main function *)
let f nums =
  let countedj = 
    List.map (fun n -> (count n nums, n)) nums
    |> List.sort_uniq (fun (c1, n1) (c2, n2) -> 
         if c1 <> c2 then compare c2 c1  (* Reverse sort by count *)
         else compare n1 n2)             (* Regular sort by number if counts equal *)
  in
  counted

(* Test the function *)
let () = 
  let result = f [1; 1; 3; 1; 3; 1] in
  result |> List.iter (fun (count, num) -> 
    Printf.printf "(%d, %d); " count num);
  print_newline ()"""

loop = """(* This function calls itself recursively with no termination *)
let rec loop () = loop ();;

let () = loop ()"""

if __name__ == "__main__":
    codes = parallel_run_ocaml([code, code, code])
    for output, error in codes:
        print(output)
        print("-")
        print(error)
        print("-"*100)

# output, error = run_ocaml(code)
# print(output)
# print("-"*100)
# print(error)
# output, error = run_ocaml(loop)
# print(output)
# print("-"*100)
# print(error)