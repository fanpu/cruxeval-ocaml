import subprocess
import tempfile
from diskcache import Cache
import json
import os
import argparse
from concurrent.futures import ProcessPoolExecutor

def sandbox_code(code):
    # Approach similar to https://ctftime.org/writeup/28166
    return f"""
module Overwritten = struct
    module Blocked = struct end
    let blocked = `Blocked_for_sandboxing
    (* File opening/creation *)
    let open_descriptor_out = blocked
    let open_descriptor_in = blocked
    let open_out = blocked
    let open_out_bin = blocked
    let open_out_gen = blocked
    let open_in = blocked
    let open_in_bin = blocked
    let open_in_gen = blocked
    let open_desc = blocked

    (* File operations *)
    let flush = blocked
    let flush_all = blocked
    let output = blocked
    let output_bytes = blocked
    let output_string = blocked
    let output_substring = blocked
    let output_char = blocked
    let output_byte = blocked
    let output_binary_int = blocked
    let output_value = blocked
    let marshal_to_channel = blocked
    let seek_out = blocked
    let pos_out = blocked
    let out_channel_length = blocked
    let close_out = blocked
    let close_out_channel = blocked
    let close_out_noerr = blocked
    let input = blocked
    let input_char = blocked
    let input_byte = blocked
    let input_binary_int = blocked
    let input_value = blocked
    let input_line = blocked
    let input_scan_line = blocked
    let really_input = blocked
    let really_input_string = blocked
    let unsafe_input = blocked
    let unsafe_really_input = blocked
    let seek_in = blocked
    let pos_in = blocked
    let in_channel_length = blocked
    let close_in = blocked
    let close_in_noerr = blocked

    (* System operations *)
    let sys_exit = blocked
    let exit = blocked
    let at_exit = blocked
    let register_named_value = blocked

    (* Could be used for nefarious things *)
    module Sys = Blocked
    module Filename = Blocked
    module Marshal = Blocked
    module Callback = Blocked
    module Gc = Blocked
    module Domain = Blocked
    module Effect = Blocked
    module Out_channel = Blocked
    module In_channel = Blocked
    module Scanf = Blocked
    module Format = Blocked
    module Obj = Blocked
end

include Overwritten
{code}
"""


def run_ocaml(code_snippet, dir, cache_name="ocaml_cache"):
    with Cache(cache_name) as db:
        key = code_snippet
        if key in db:
            result = json.loads(db[key].decode("utf-8"))
            return result[0], result[1]

        # Create a temporary file with the code snippet
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ml", delete=False, dir=dir
        ) as temp_file:
            temp_file.write(sandbox_code(code_snippet))
            temp_filename = temp_file.name[len(dir) + 1 :]

        try:
            # Run the OCaml compiler on the temporary file
            result = subprocess.run(
                ["ocaml", temp_filename],
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

        return output, error


def parallel_run_ocaml(queries, dir, max_workers=None) -> tuple[bool, str]:
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_ocaml, query, dir) for query in queries]
        results = [future.result() for future in futures]
    return results


code = """(* Helper function to count occurrences of an element in a list *)
let count x lst =
  List.fold_left (fun acc elem -> if elem = x then acc + 1 else acc) 0 lst

(* Main function *)
let f nums =
  let counted = 
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

malicious = """
let print_file filename =
  let channel = open_in filename in
  try
    while true do
      let line = input_line channel in
      print_endline line
    done
  with End_of_file ->
    close_in channel

let () =
  print_file "/etc/passwd"
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run OCaml code snippets")
    parser.add_argument(
        "--dir",
        type=str,
        help="Directory for temporary files for executing code snippets",
        required=True,
    )
    args = parser.parse_args()

    codes = parallel_run_ocaml([code, code, code], args.dir)
    for output, error in codes:
        print("output", output)
        print("-")
        print("error", error)
        print("-" * 100)

    # Running this should return an error
    print(parallel_run_ocaml([malicious], args.dir))