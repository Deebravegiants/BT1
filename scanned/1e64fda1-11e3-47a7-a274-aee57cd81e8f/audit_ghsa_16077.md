# [M] Improper Authorization in dolibarr/dolibarr

## Summary
Severity: Medium
Advisory: GHSA-wppr-j57c-8jpm
CVE: CVE-2021-3991
CWE: CWE-285, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-wppr-j57c-8jpm
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <15.0.0

## Details
An Improper Authorization vulnerability exists in Dolibarr versions prior to version 15.0.0. A user with restricted permissions in the 'Reception' section is able to access specific reception details via direct URL access, bypassing the intended permission restrictions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3991
- https://github.com/dolibarr/dolibarr/commit/63cd06394f39d60784d6e6a0ccf4867a71a6568f
- https://github.com/dolibarr/dolibarr
- https://huntr.com/bounties/58ddbd8a-0faf-4b3f-aec9-5850bb19ab67
