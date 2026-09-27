# [H] Webkul Krayin CRM has Broken Object-Level Authorization (BOLA) in the /Settings/UserController.php

## Summary
Severity: High
Advisory: GHSA-r8rp-5f55-5j9x
CVE: CVE-2026-38529
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-r8rp-5f55-5j9x
Type: github-advisory

## Affected
- Packagist: `krayin/laravel-crm` — affected >=0

## Details
A Broken Object-Level Authorization (BOLA) in the /Settings/UserController.php endpoint of Webkul Krayin CRM v2.2.x allows authenticated attackers to arbitrarily reset user passwords and perform a full account takeover via supplying a crafted HTTP request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38529
- https://github.com/TREXNEGRO/Security-Advisories/tree/main/CVE-2026-38529
- https://github.com/krayin/laravel-crm
