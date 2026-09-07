# [M] Dolibarr ERP CRM Code Injection vulnerability during installation

## Summary
Severity: Medium
Advisory: GHSA-p73x-rpgm-3v56
CVE: CVE-2024-29477
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-03
Source: https://github.com/advisories/GHSA-p73x-rpgm-3v56
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0

## Details
Lack of sanitization during Installation Process in Dolibarr ERP CRM up to version 19.0.0 allows an attacker with adjacent access to the network to execute arbitrary code via a specifically crafted input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29477
- https://github.com/Dolibarr/dolibarr
- https://github.com/alexbsec/CVEs/blob/master/2024/CVE-2024-29477.md
- http://dolibarr.com
