# [H] Lavalite vulnerable to Arbitrary File Read via Directory Traversal

## Summary
Severity: High
Advisory: GHSA-cm22-88qr-7ffh
CVE: CVE-2022-42188
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-cm22-88qr-7ffh
Type: github-advisory

## Affected
- Packagist: `lavalite/cms` — affected 9.0.0

## Details
In Lavalite 9.0.0, the XSRF-TOKEN cookie is vulnerable to path traversal attacks, enabling read access to arbitrary files on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42188
- https://github.com/LavaLite/cms
- https://github.com/nu11secur1ty/CVE-nu11secur1ty/tree/main/vendors/LavaLite
