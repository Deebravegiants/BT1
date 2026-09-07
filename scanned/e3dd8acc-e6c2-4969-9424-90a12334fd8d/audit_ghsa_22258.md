# [H] Dolibarr ERP and CRM malicious executable loading

## Summary
Severity: High
Advisory: GHSA-2rwh-262r-r85j
CVE: CVE-2019-11200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2rwh-262r-r85j
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <9.0.3

## Details
Dolibarr ERP/CRM 9.0.1 provides a web-based functionality that backs up the database content to a dump file. However, the application performs insufficient checks on the export parameters to mysqldump, which can lead to execution of arbitrary binaries on the server. (Malicious binaries can be uploaded by abusing other functionalities of the application.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11200
- https://github.com/Dolibarr/dolibarr/issues/10984#issuecomment-488297419
- https://github.com/Dolibarr/dolibarr/commit/01075081cbcd9130a72115cdb50ee61fc394edc1
- https://github.com/Dolibarr/dolibarr/commit/d6ae62478c8841fdfe58971494818b599f396d4f
- https://github.com/Dolibarr/dolibarr
- https://know.bishopfox.com/advisories/dolibarr-version-9-0-1-vulnerabilities
