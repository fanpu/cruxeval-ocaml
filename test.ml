let f (text : string) : string =
  let processed = String.trim (String.lowercase_ascii text) in
  let valid_chars = ['A'; 'a'] in
  String.to_seq processed
  |> Seq.filter (fun ch ->
         match ch with
         | ch when ch >= '0' && ch <= '9' -> true
         | ch when List.mem ch valid_chars -> true
         | _ -> false)
  |> String.of_seq

let () =
  let result = f "" in
  assert (result = "")


