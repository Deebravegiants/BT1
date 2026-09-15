# [H] Directory Traversal vulnerability in serve-lite

## Summary
Severity: High
Advisory: GHSA-5qq4-m6c3-xxmf
CVE: CVE-2022-21192
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-5qq4-m6c3-xxmf
Type: github-advisory

## Affected
- npm: `serve-lite` — affected >=0

## Details
All versions of the package serve-lite are vulnerable to Directory Traversal due to missing input sanitization or other checks and protections employed to the req.url passed as-is to path.join().

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21192
- https://gist.github.com/lirantal/9ccdfda0edcb95e36d07a04b0b6c2db0
- https://github.com/beenotung/serve-lite
- https://security.snyk.io/vuln/SNYK-JS-SERVELITE-3149916
