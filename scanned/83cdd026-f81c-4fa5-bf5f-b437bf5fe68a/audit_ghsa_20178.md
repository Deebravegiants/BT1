# [H] OS Command injection in ssl-utils

## Summary
Severity: High
Advisory: GHSA-552j-pv39-f3jf
CVE: CVE-2021-34080
CWE: CWE-78
Ecosystem: npm
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-552j-pv39-f3jf
Type: github-advisory

## Affected
- npm: `ssl-utils` — affected >=0

## Details
OS Command Injection vulnerability in es128 ssl-utils 1.0.0 for Node.js allows attackers to execute arbitrary commands via unsanitized shell metacharacters provided to the createCertRequest() and the createCert() functions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34080
- https://advisory.checkmarx.net/advisory/CX-2021-4782
- https://github.com/es128/ssl-utils
