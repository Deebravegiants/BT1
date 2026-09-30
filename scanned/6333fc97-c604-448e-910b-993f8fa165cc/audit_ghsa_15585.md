# [H] Mesop has a local file Inclusion via static file serving functionality

## Summary
Severity: High
Advisory: GHSA-pmv9-3xqp-8w42
CVE: CVE-2024-45601
CWE: CWE-20, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-pmv9-3xqp-8w42
Type: github-advisory

## Affected
- PyPI: `mesop` — affected >=0.9.0 <0.12.4

## Details
A vulnerability has been discovered and fixed in Mesop that could potentially allow unauthorized access to files on the server hosting the Mesop application. The vulnerability was related to insufficient input validation in a specific endpoint. This could have allowed an attacker to access files not intended to be served.

Users are strongly advised to update to the latest version of Mesop immediately. The latest version includes a fix for this vulnerability.

We would like to thank @Letm3through for reporting this issue and proposing mitigations to address this issue.

## References
- https://github.com/google/mesop/security/advisories/GHSA-pmv9-3xqp-8w42
- https://nvd.nist.gov/vuln/detail/CVE-2024-45601
- https://github.com/google/mesop/commit/17fb769d6a91f0a8cbccfab18f64977b158a6a31
- https://github.com/google/mesop
