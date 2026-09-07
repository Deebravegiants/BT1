# [M] Dolibarr allows password changes without supplying the current password

## Summary
Severity: Medium
Advisory: GHSA-5x4j-xcmv-v3q2
CVE: CVE-2017-8879
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5x4j-xcmv-v3q2
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected 4.0.4

## Details
Dolibarr ERP/CRM 4.0.4 allows password changes without supplying the current password, which makes it easier for physically proximate attackers to obtain access via an unattended workstation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8879
- https://github.com/Dolibarr/dolibarr
- https://www.foxmole.com/advisories/foxmole-2017-02-23.txt
