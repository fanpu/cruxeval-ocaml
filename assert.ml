(* Define a function to count occurrences of a given element in a list *)
let count x lst =
  List.fold_left (fun acc y -> if y = x then acc + 1 else acc) 0 lst

(* Function f: Takes a list of ints and produces a list of pairs (count, element) *)
let f nums =
  (* Create a list of tuples: (frequency count, element) for each element in nums *)
  let output = List.map (fun n -> (count n nums, n)) nums in
  (* Sort the list in descending order based on the frequency (and then by the element if needed) *)
  let compare (c1, n1) (c2, n2) =
    let res = compare c2 c1 in (* reverse order by count *)
    if res = 0 then compare n2 n1 else res  (* secondary order: descending by element *)
  in
  List.sort compare output

let () =
  let result = f [1; 1; 3; 1; 3; 1] in
  assert (result = [(4, 1); (4, 1); (4, 1); (4, 1); (2, 3); (2, 3)]);