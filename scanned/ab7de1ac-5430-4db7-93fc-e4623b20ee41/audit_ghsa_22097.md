# [C] Dolibarr ERP and CRM SQLi

## Summary
Severity: Critical
Advisory: GHSA-v3m8-7h3p-6j5m
CVE: CVE-2017-9435
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v3m8-7h3p-6j5m
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <5.0.3

## Details
Dolibarr ERP/CRM before 5.0.3 is vulnerable to a SQL injection in user/index.php (search_supervisor and search_statut parameters).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9435
- https://github.com/Dolibarr/dolibarr/commit/70636cc59ffa1ffbc0ce3dba315d7d9b837aad04
- https://github.com/Dolibarr/dolibarr/blob/develop/ChangeLog
