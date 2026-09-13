# [H] m.static Directory Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-vcxh-qvgr-9fw9
CVE: CVE-2023-26126
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-10
Source: https://github.com/advisories/GHSA-vcxh-qvgr-9fw9
Type: github-advisory

## Affected
- npm: `m.static` — affected >=0

## Details
All versions of the package m.static are vulnerable to Directory Traversal due to improper input sanitization of the path being requested via the `requestFile` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26126
- https://gist.github.com/lirantal/dcb32c11ce87f5aafd2282b90b4dc998
- https://github.com/ivoputzer/m.static
- https://github.com/ivoputzer/m.static/blob/master/index.js#L19
- https://security.snyk.io/vuln/SNYK-JS-MSTATIC-3244915
