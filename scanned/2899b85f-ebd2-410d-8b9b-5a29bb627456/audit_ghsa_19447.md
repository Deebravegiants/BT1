# [M] estree-util-value-to-estree allows prototype pollution in generated ESTree

## Summary
Severity: Medium
Advisory: GHSA-f7f6-9jq7-3rqj
CVE: CVE-2025-32014
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-f7f6-9jq7-3rqj
Type: github-advisory

## Affected
- npm: `estree-util-value-to-estree` — affected >=0 <3.3.3

## Details
### Impact
When generating an ESTree from a value with a property named `__proto__`, `valueToEstree` would generate an object that specifies a prototype instead.

Example:

```js
import { generate } from 'astring'
import { valueToEstree } from 'estree-util-value-to-estree'

const estree = valueToEstree({
  ['__proto__']: {}
})
const code = generate(estree)
console.log(code)
```

Output:

```js
{
  "__proto__": {}
}
```

### Patches
This was fixed in version [3.3.3](https://github.com/remcohaszing/estree-util-value-to-estree/releases/tag/v3.3.3).

### Workarounds
If you control the input, don’t specify a property named `__proto__`. If you don’t control the output, strip any properties named `__proto__` before passing it to `valueToEstree`.

## References
- https://github.com/remcohaszing/estree-util-value-to-estree/security/advisories/GHSA-f7f6-9jq7-3rqj
- https://nvd.nist.gov/vuln/detail/CVE-2025-32014
- https://github.com/remcohaszing/estree-util-value-to-estree/commit/d0c394fbc64bc55937ffe4e162b81f15ba506e55
- https://github.com/remcohaszing/estree-util-value-to-estree
