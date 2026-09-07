# [M] qs's arrayLimit bypass in its bracket notation allows DoS via memory exhaustion

## Summary
Severity: Medium
Advisory: GHSA-6rw7-vpxm-498p
CVE: CVE-2025-15284
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-6rw7-vpxm-498p
Type: github-advisory

## Affected
- npm: `qs` — affected >=0 <6.14.1

## Details
### Summary

The `arrayLimit` option in qs did not enforce limits for bracket notation (`a[]=1&a[]=2`), only for indexed notation (`a[0]=1`). This is a consistency bug; `arrayLimit` should apply uniformly across all array notations.

**Note:** The default `parameterLimit` of 1000 effectively mitigates the DoS scenario originally described. With default options, bracket notation cannot produce arrays larger than `parameterLimit` regardless of `arrayLimit`, because each `a[]=value` consumes one parameter slot. The severity has been reduced accordingly.

### Details

The `arrayLimit` option only checked limits for indexed notation (`a[0]=1&a[1]=2`) but did not enforce it for bracket notation (`a[]=1&a[]=2`).

**Vulnerable code** (`lib/parse.js:159-162`):
```javascript
if (root === '[]' && options.parseArrays) {
    obj = utils.combine([], leaf);  // No arrayLimit check
}
```

**Working code** (`lib/parse.js:175`):
```javascript
else if (index <= options.arrayLimit) {  // Limit checked here
    obj = [];
    obj[index] = leaf;
}
```

The bracket notation handler at line 159 uses `utils.combine([], leaf)` without validating against `options.arrayLimit`, while indexed notation at line 175 checks `index <= options.arrayLimit` before creating arrays.

### PoC

```javascript
const qs = require('qs');
const result = qs.parse('a[]=1&a[]=2&a[]=3&a[]=4&a[]=5&a[]=6', { arrayLimit: 5 });
console.log(result.a.length);  // Output: 6 (should be max 5)
```

**Note on parameterLimit interaction:** The original advisory's "DoS demonstration" claimed a length of 10,000, but `parameterLimit` (default: 1000) caps parsing to 1,000 parameters. With default options, the actual output is 1,000, not 10,000.

### Impact

Consistency bug in `arrayLimit` enforcement. With default `parameterLimit`, the practical DoS risk is negligible since `parameterLimit` already caps the total number of parsed parameters (and thus array elements from bracket notation). The risk increases only when `parameterLimit` is explicitly set to a very high value.

## References
- https://github.com/ljharb/qs/security/advisories/GHSA-6rw7-vpxm-498p
- https://nvd.nist.gov/vuln/detail/CVE-2025-15284
- https://github.com/ljharb/qs/commit/3086902ecf7f088d0d1803887643ac6c03d415b9
- https://github.com/ljharb/qs
