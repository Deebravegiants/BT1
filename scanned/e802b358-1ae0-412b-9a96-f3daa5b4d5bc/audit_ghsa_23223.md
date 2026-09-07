# [H] Dolibarr sensitive information disclosure

## Summary
Severity: High
Advisory: GHSA-jm38-vmgp-j7rx
CVE: CVE-2017-17898
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-jm38-vmgp-j7rx
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <6.0.5

## Details
Dolibarr ERP/CRM version 6.0.4 does not block direct requests to *.tpl.php files, which allows remote attackers to obtain sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17898
- https://github.com/Dolibarr/dolibarr/commit/4a5988accbb770b74105baacd5a034689272128c
- https://github.com/Dolibarr/dolibarr/commit/6a62e139604dbbd5729e57df2433b37a5950c35c
- https://github.com/Dolibarr/dolibarr
