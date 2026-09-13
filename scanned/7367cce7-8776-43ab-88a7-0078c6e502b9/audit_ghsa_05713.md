# [M] Maker.js has Unsafe Property Copying in makerjs.extendObject

## Summary
Severity: Medium
Advisory: GHSA-2cp6-34r9-54xx
CVE: CVE-2026-24888
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-29
Source: https://github.com/advisories/GHSA-2cp6-34r9-54xx
Type: github-advisory

## Affected
- npm: `makerjs` — affected >=0 <0.19.2

## Details
### Summary
The `makerjs.extendObject` function copies properties from source objects without proper validation, potentially exposing applications to security risks. The function lacks `hasOwnProperty()` checks and does not filter dangerous keys, allowing inherited properties and potentially malicious properties to be copied to target objects.

### Details
The `extendObject` function iterates over source object properties using a `for...in` loop without:
1. Checking `hasOwnProperty()` to exclude inherited properties
2. Filtering dangerous keys (`__proto__`, `constructor`, `prototype`)
3. Validating property sources

### Affected Code

**File**: https://github.com/microsoft/maker.js/blob/98cffa82a372ff942194c925a12a311253587167/packages/maker.js/src/core/maker.ts#L232-L241



### PoC
```javascript
const makerjs = require('makerjs');

const source = { __proto__: { name: 'Ravi', isAdmin: true } };
const target = { name: 'user' };
const result = makerjs.extendObject(target, source);

console.log(result.name);  // Ravi
console.log(result.isAdmin);   // true
```


### Impact
### Security Implications

1. **Unexpected Behavior**: Properties may appear on target objects but not be own properties, breaking `hasOwnProperty()` assumptions in security-sensitive code.

2. **Security Bypass Risk**: Code relying on `hasOwnProperty()` for validation could be bypassed.

3. **Future Risk**: Lack of dangerous key filtering (`__proto__`, `constructor`, `prototype`) exposes potential attack vectors.

### Affected Use Cases

- Extending objects from user input or external APIs
- Merging options from untrusted sources

## References
- https://github.com/microsoft/maker.js/security/advisories/GHSA-2cp6-34r9-54xx
- https://nvd.nist.gov/vuln/detail/CVE-2026-24888
- https://github.com/microsoft/maker.js/commit/85e0f12bd868974b891601a141974f929dec36b8
- https://github.com/microsoft/maker.js
- https://github.com/microsoft/maker.js/blob/98cffa82a372ff942194c925a12a311253587167/packages/maker.js/src/core/maker.ts#L232-L241
