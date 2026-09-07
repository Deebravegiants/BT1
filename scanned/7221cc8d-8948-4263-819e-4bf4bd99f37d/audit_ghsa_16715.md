# [C] Dolibarr vulnerable to SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-q8x7-jc3h-p8xc
CVE: CVE-2024-5315
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-24
Source: https://github.com/advisories/GHSA-q8x7-jc3h-p8xc
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0

## Details
Vulnerabilities in Dolibarr ERP - CRM that affect version 9.0.1 and allow SQL injection. These vulnerabilities could allow a remote attacker to send a specially crafted SQL query to the system and retrieve all the information stored in the database through the parameters in /dolibarr/commande/list.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5315
- https://github.com/Dolibarr/dolibarr
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-dolibarrs-erp-cms
