# [C] Dolibarr ERP CRM contains a remote code evaluation vulnerability

## Summary
Severity: Critical
Advisory: GHSA-hxmh-2xc4-c894
CVE: CVE-2018-25357
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-hxmh-2xc4-c894
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=7.0.0 <7.0.4
- Packagist: `dolibarr/dolibarr` — affected >=0 <6.0.8

## Details
Dolibarr ERP CRM 7.0.3 contains a remote code evaluation vulnerability that allows unauthenticated attackers to execute arbitrary code by injecting PHP code through the db_name parameter. Attackers can send a POST request to install/step1.php with malicious PHP code in the db_name parameter, then execute commands via the check.php endpoint using the cmd GET parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25357
- https://github.com/Dolibarr/dolibarr/issues/9032
- https://github.com/Dolibarr/dolibarr/commit/41709f07d0aef384723164877395ed081b44b810
- https://dolibarr.org
- https://github.com/Dolibarr/dolibarr
- https://www.exploit-db.com/exploits/44964
- https://www.vulncheck.com/advisories/dolibarr-erp-crm-remote-code-evaluation-via-install-step1-php
