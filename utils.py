import re

def remove_ocaml_comments(ocaml_code):
    pattern = re.compile(r'\(\*.*?\*\)', re.DOTALL)
    
    # Remove all comments
    def replacer(match):
        comment = match.group(0)
        if '\n' in comment:  # Multi-line comment, replace with newlines to preserve structure
            return '\n' * comment.count('\n')
        return ''  # Single-line inline comment, remove completely
    
    cleaned_code = pattern.sub(replacer, ocaml_code)
    
    # Remove completely empty lines
    cleaned_code = '\n'.join(line for line in cleaned_code.splitlines() if line.strip())
    
    return cleaned_code