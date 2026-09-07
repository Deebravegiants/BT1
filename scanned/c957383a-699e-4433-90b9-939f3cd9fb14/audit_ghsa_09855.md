# [H] Webkul Krayin CRM has Broken Object-Level Authorization (BOLA) in the /Contact/Persons/PersonController.php

## Summary
Severity: High
Advisory: GHSA-2xx8-j85v-j7wh
CVE: CVE-2026-38532
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-2xx8-j85v-j7wh
Type: github-advisory

## Affected
- Packagist: `krayin/laravel-crm` — affected >=0

## Details
A Broken Object-Level Authorization (BOLA) in the /Contact/Persons/PersonController.php endpoint of Webkul Krayin CRM v2.2.x allows authenticated attackers to arbitrarily read, modify, and permanently delete any contact owned by other users via supplying a crafted GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38532
- https://github.com/TREXNEGRO/Security-Advisories/tree/main/CVE-2026-38532
- https://github.com/krayin/laravel-crm
