# [H] DataFlow upload remote code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-h632-p764-pjqm
CVE: CVE-2021-41231
CWE: CWE-434, CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-27
Source: https://github.com/advisories/GHSA-h632-p764-pjqm
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <19.4.22
- Packagist: `openmage/magento-lts` — affected >=20.0.0 <20.0.19

## Details
### Impact
An administrator with the permissions to upload files via DataFlow and to create products was able to execute arbitrary code via the convert profile.

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-h632-p764-pjqm
- https://nvd.nist.gov/vuln/detail/CVE-2021-41231
- https://github.com/OpenMage/magento-lts/commit/d16fc6c5a1e66c6f0d9f82020f11702a7ddd78e4
- https://github.com/OpenMage/magento-lts
- https://github.com/OpenMage/magento-lts/releases/tag/v19.4.22
- https://github.com/OpenMage/magento-lts/releases/tag/v20.0.19
