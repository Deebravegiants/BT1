# [H] Path Traversal in Payara

## Summary
Severity: High
Advisory: GHSA-h28c-453m-h9xm
CVE: CVE-2022-37422
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-08-19
Source: https://github.com/advisories/GHSA-h28c-453m-h9xm
Type: github-advisory

## Affected
- Maven: `fish.payara.api:payara-bom` — affected >=0 <5.2022.3

## Details
Payara through 5.2022.2 allows directory traversal without authentication. This affects Payara Server, Payara Micro, and Payara Server Embedded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37422
- https://blog.payara.fish/august-community-5-release
