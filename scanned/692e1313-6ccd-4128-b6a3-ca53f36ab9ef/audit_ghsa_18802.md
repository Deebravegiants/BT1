# [H] Dolibarr vulnerable to RCE via the computed field parameter

## Summary
Severity: High
Advisory: GHSA-27hj-48r9-x2vx
CVE: CVE-2025-56588
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-01
Source: https://github.com/advisories/GHSA-27hj-48r9-x2vx
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <21.0.3

## Details
Dolibarr ERP & CRM v21.0.1 were discovered to contain a remote code execution (RCE) vulnerability in the User module configuration via the computed field parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56588
- https://github.com/Dolibarr/dolibarr/commit/b03f30c7e27fb89dbfb15902dbf4619ae77f0f86
- https://github.com/Dolibarr/dolibarr
- https://github.com/PhDg1410/Research
- http://dolibarr.com
