# [H] Inefficient Regular Expression Complexity in node-email-check

## Summary
Severity: High
Advisory: GHSA-9242-6p36-6256
CVE: CVE-2023-39619
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-9242-6p36-6256
Type: github-advisory

## Affected
- npm: `node-email-check` — affected >=0

## Details
ReDos in NPMJS Node Email Check v.1.0.4 allows an attacker to cause a denial of service via a crafted string to the scpSyntax component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39619
- https://github.com/teomantuncer/node-email-check/issues/2
- https://gist.github.com/6en6ar/712a4c1eab0324f15e09232c77ea08f8
- https://github.com/teomantuncer/node-email-check
- https://www.npmjs.com/package/node-email-check
