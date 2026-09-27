# [M] crypto-js uses insecure random numbers

## Summary
Severity: Medium
Advisory: GHSA-3w3w-pxmm-2w2j
CVE: CVE-2020-36732
CWE: CWE-330, CWE-331
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-06-12
Source: https://github.com/advisories/GHSA-3w3w-pxmm-2w2j
Type: github-advisory

## Affected
- npm: `crypto-js` — affected >=3.2.0 <3.2.1

## Details
The crypto-js package 3.2.0 for Node.js generates random numbers by concatenating the string "0." with an integer, which makes the output more predictable than necessary.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36732
- https://github.com/brix/crypto-js/issues/254
- https://github.com/brix/crypto-js/issues/256
- https://github.com/brix/crypto-js/pull/257/commits/e4ac157d8b75b962d6538fc0b996e5d4d5a9466b
- https://github.com/brix/crypto-js/commit/b405ff597fb3ac76a7bdfbc72dca10ba1079b1d5
- https://github.com/brix/crypto-js/commit/e4ac157d8b75b962d6538fc0b996e5d4d5a9466b
- https://github.com/brix/crypto-js
- https://github.com/brix/crypto-js/compare/3.2.0...3.2.1
- https://security.netapp.com/advisory/ntap-20230706-0003
- https://security.snyk.io/vuln/SNYK-JS-CRYPTOJS-548472
