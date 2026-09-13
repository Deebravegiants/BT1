# [H] Masa CMS vulnerable to authentication bypass with /tag/

## Summary
Severity: High
Advisory: CVE-2024-32643
Aliases: GHSA-f469-jh82-97fv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/CVE-2024-32643
Type: osv

## Details
Masa CMS is an open source Enterprise Content Management platform. Prior to 7.2.8, 7.3.13, and 7.4.6, if the URL to the page is modified to include a /tag/ declaration, the CMS will render the page regardless of group restrictions. This vulnerability is fixed in 7.2.8, 7.3.13, and 7.4.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32643.json
- https://github.com/MasaCMS/MasaCMS/security/advisories/GHSA-f469-jh82-97fv
- https://nvd.nist.gov/vuln/detail/CVE-2024-32643
- https://github.com/MasaCMS/MasaCMS/commit/d1a2e57ef8dbc50c87b178eacc85fcccb05f5b6c
