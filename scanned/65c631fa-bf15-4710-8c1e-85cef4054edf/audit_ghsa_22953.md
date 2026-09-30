# [H] Uncaught Exception in bignum

## Summary
Severity: High
Advisory: GHSA-6429-3g3w-6mw5
CVE: CVE-2022-25324
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-07
Source: https://github.com/advisories/GHSA-6429-3g3w-6mw5
Type: github-advisory

## Affected
- npm: `bignum` — affected >=0

## Details
All versions of the npm package bignum are vulnerable to Denial of Service (DoS) due to a type-check exception in V8. When verifying the type of the second argument to the .powm function, V8 will crash regardless of Node try/catch blocks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25324
- https://github.com/justmoon/node-bignum
- https://github.com/justmoon/node-bignum/blob/ef2e02533e598d6df8421000033c4753cde89ee2/index.js#L111
- https://snyk.io/vuln/SNYK-JS-BIGNUM-2388581
