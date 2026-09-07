# [H] Insecure Comparison in secure-compare

## Summary
Severity: High
Advisory: GHSA-h9x2-5rm7-x4gm
CVE: CVE-2015-9238
CWE: CWE-697
Ecosystem: npm
Published: 2019-06-03
Source: https://github.com/advisories/GHSA-h9x2-5rm7-x4gm
Type: github-advisory

## Affected
- npm: `secure-compare` — affected >=0 <3.0.1

## Details
Versions of `secure-compare` prior to 3.0.1 are affected by a vulnerability that results in the package always returning true when comparing two strings of the same length, despite differences in the contents of those strings.


## Recommendation

Upgrade to version 3.0.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9238
- https://github.com/vdemedes/secure-compare/pull/1
- https://github.com/vadimdemedes/secure-compare/commit/dd1ff1ac0122de7e0af4f00c61ed73261062394a
- https://www.npmjs.com/advisories/50
