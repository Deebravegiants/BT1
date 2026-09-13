# [M] Parse Server has a LiveQuery protected-field guard bypass via array-like logical operator value

## Summary
Severity: Medium
Advisory: GHSA-mmg8-87c5-jrc2
CVE: CVE-2026-34595
CWE: CWE-843
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-mmg8-87c5-jrc2
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.7.0-alpha.16
- npm: `parse-server` — affected >=0 <8.6.70

## Details
### Impact

An authenticated user with `find` class-level permission can bypass the `protectedFields` class-level permission setting on LiveQuery subscriptions. By sending a subscription with a `$or`, `$and`, or `$nor` operator value as a plain object with numeric keys and a `length` property (an "array-like" object) instead of an array, the protected-field guard is bypassed. The subscription event firing acts as a binary oracle, allowing the attacker to infer whether a protected field matches a given test value.

### Patches

The fix validates that `$or`, `$and`, and `$nor` operator values are arrays in the LiveQuery subscription handler, the query depth checker, and the protected-field guard. As defense in depth, the LiveQuery query evaluator also rejects non-array values for these operators.

### Workarounds

There is no known workaround.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-mmg8-87c5-jrc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-34595
- https://github.com/parse-community/parse-server/pull/10350
- https://github.com/parse-community/parse-server/pull/10351
- https://github.com/parse-community/parse-server/commit/f63fd1a3fe0a7c1c5fe809f01b0e04759e8c9b98
- https://github.com/parse-community/parse-server/commit/ffad0ec6b971ee0dd9545e1bf1fb34ddebf275c2
- https://github.com/parse-community/parse-server
