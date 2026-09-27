# [M] qs array-limit bypass via bracket-key comma parsing

## Summary
Severity: Medium
Advisory: GHSA-x5fp-wj9c-mxmx
CVE: CVE-2026-82562
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-x5fp-wj9c-mxmx
Type: github-advisory

## Affected
- npm: `qs` — affected >=6.14.2 <6.16.0

## Details
### Summary

`qs` `v6.15.3` allows bracket-key input to bypass `arrayLimit` and `throwOnLimitExceeded` when `comma: true`. The input `a[]=1,2,3,4` succeeds with `arrayLimit: 3`, while the equivalent plain-key input is rejected.

Affected version tested:

```text
qs v6.15.3
commit 18d085e919dae70c8f1b200ab99323058edab2c2
```

### Details

`parseArrayValue()` enforces the comma limit only for flat values. The `a[]` form is marked non-flat, so its comma-separated value is wrapped after parsing and the inner array is not checked. A single parameter can therefore materialize arbitrarily large arrays.

### PoC

```js
const qs = require('qs')
const options = { comma: true, arrayLimit: 3, throwOnLimitExceeded: true }

const result = qs.parse('a[]=1,2,3,4', options)
console.log(result.a[0].length) // 4; expected RangeError

const big = qs.parse('a[]=' + '1,'.repeat(1000000) + '1', { comma: true, arrayLimit: 20 })
console.log(big.a[0].length) // 1000001
```

On `v6.15.3`, the first input parses successfully and the second creates an array with 1,000,001 elements. The equivalent `a=1,2,3,4` input throws `RangeError` as expected.

### Impact

An attacker who can supply a query string or form body can bypass configured array limits and force excessive memory allocation, causing denial of service. The limit must be applied after comma splitting and before the resulting array is wrapped.

## References
- https://github.com/ljharb/qs/security/advisories/GHSA-w7fw-mjwx-w883
- https://github.com/ljharb/qs/security/advisories/GHSA-x5fp-wj9c-mxmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-82562
- https://github.com/ljharb/qs/commit/8859c37470e11b42b547b275e4e9bd0bc8cc5464
- https://github.com/ljharb/qs
