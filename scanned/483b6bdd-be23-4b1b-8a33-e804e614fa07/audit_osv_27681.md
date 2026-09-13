# [H] Galette public pages accessibility restriction

## Summary
Severity: High
Advisory: CVE-2024-24761
Aliases: GHSA-jrqg-mpwv-pxpv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2024-24761
Type: osv

## Details
Galette is a membership management web application for non profit organizations. Starting in version 1.0.0 and prior to version 1.0.2, public pages are per default restricted to only administrators and staff members. From configuration, it is possible to restrict to up-to-date members or to everyone. Version 1.0.2 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24761.json
- https://github.com/galette/galette/security/advisories/GHSA-jrqg-mpwv-pxpv
- https://nvd.nist.gov/vuln/detail/CVE-2024-24761
- https://github.com/galette/galette/commit/a5c18bb9819b8da1b3ef58f3e79577083c657fbb
