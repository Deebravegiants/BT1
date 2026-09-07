# [H] Dolibarr ERP and CRM Sensitive Data Disclosure

## Summary
Severity: High
Advisory: GHSA-p9wf-x8h5-44fr
CVE: CVE-2017-14240
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p9wf-x8h5-44fr
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <6.0.1

## Details
There is a sensitive information disclosure vulnerability in document.php in Dolibarr ERP/CRM version 6.0.0 via the file parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14240
- https://github.com/Dolibarr/dolibarr/commit/d26b2a694de30f95e46ea54ea72cc54f0d38e548
