# [C] Elefant CMS Improper Input Validation

## Summary
Severity: Critical
Advisory: GHSA-pcf7-5974-vjh4
CVE: CVE-2018-15601
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-pcf7-5974-vjh4
Type: github-advisory

## Affected
- Packagist: `elefant/cms` — affected >=0 <2.0.4

## Details
`apps/filemanager/handlers/upload/drop.php` in Elefant CMS 2.0.3 performs a urldecode step too late in the "Cannot upload executable files" protection mechanism.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15601
- https://github.com/jbroadway/elefant/commit/afb3346e50b992bcba143660ca2149e563430e05
