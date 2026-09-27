# [H] Webkul Krayin CRM has Server-Side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: GHSA-fpx9-9hq8-w2xc
CVE: CVE-2026-38527
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-fpx9-9hq8-w2xc
Type: github-advisory

## Affected
- Packagist: `krayin/laravel-crm` — affected >=0

## Details
A Server-Side Request Forgery (SSRF) in the /settings/webhooks/create component of Webkul Krayin CRM v2.2.x allows attackers to scan internal resources via supplying a crafted POST request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38527
- https://github.com/TREXNEGRO/Security-Advisories/tree/main/CVE-2026-38527
- https://github.com/krayin/laravel-crm
