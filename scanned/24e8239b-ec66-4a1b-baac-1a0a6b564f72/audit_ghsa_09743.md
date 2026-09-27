# [H] Webkul Krayin CRM has Broken Object-Level Authorization (BOLA) in the /Controllers/Lead/LeadController.php

## Summary
Severity: High
Advisory: GHSA-rm5f-3c25-p4cw
CVE: CVE-2026-38530
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-rm5f-3c25-p4cw
Type: github-advisory

## Affected
- Packagist: `krayin/laravel-crm` — affected >=0

## Details
A Broken Object-Level Authorization (BOLA) in the /Controllers/Lead/LeadController.php endpoint of Webkul Krayin CRM v2.2.x allows authenticated attackers to arbitrarily read, modify, and permanently delete any lead owned by other users via supplying a crafted GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38530
- https://github.com/TREXNEGRO/Security-Advisories/tree/main/CVE-2026-38530
- https://github.com/krayin/laravel-crm
