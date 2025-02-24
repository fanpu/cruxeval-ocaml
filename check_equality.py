from run import run_ocaml
def check_equal(obj1, obj2):
    program = f"""
let obj1 = {obj1}
let obj2 = {obj2}

let () =
if obj1 = obj2 then
    print_endline "true"
else
    print_endline "false"
    """
    output, _ = run_ocaml(program)
    try:
        return output.strip() == "true"
    except:
        return False

assert check_equal("[1; 2; 3]", "[1;      2; 3]")
assert not check_equal("[1; 2; 3]", "[1;      2; 4]")
assert not check_equal("[1; 2; 3]", "'[1; 2; 3]'")