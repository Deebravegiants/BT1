# [M] Krayin CRM vulnerable to Cross Site Scripting (XSS) via the organization name

## Summary
Severity: Medium
Advisory: GHSA-74q2-6jp4-3rqq
CVE: CVE-2024-45932
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-07
Source: https://github.com/advisories/GHSA-74q2-6jp4-3rqq
Type: github-advisory

## Affected
- Packagist: `krayin/laravel-crm` — affected >=0

## Details
Krayin CRM v1.3.0 is vulnerable to Cross Site Scripting (XSS) via the organization name field in `/admin/contacts/organizations/edit/2`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45932
- https://github.com/AslamMahi/CVE-Aslam-Mahi/blob/main/Laravel%20CRM%20v1.3.0/CVE-2024-45932.md
- https://github.com/krayin/laravel-crm
- https://krayincrm.com
