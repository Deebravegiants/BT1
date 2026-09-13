# [H] Data Flow Sanitation Issue Fix 

## Summary
Severity: High
Advisory: GHSA-xm9f-vxmx-4m58
CVE: CVE-2021-32759
CWE: CWE-20
Ecosystem: Packagist
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-xm9f-vxmx-4m58
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <19.4.15
- Packagist: `openmage/magento-lts` — affected >=20.0.0 <20.0.13

## Details
### Impact
Due to missing sanitation in data flow it was possible for admin users to upload arbitrary executable files to the server.

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-xm9f-vxmx-4m58
- https://nvd.nist.gov/vuln/detail/CVE-2021-32759
- https://github.com/OpenMage/magento-lts/commit/34709ac642d554aa1824892059186dd329db744b
- https://github.com/OpenMage/magento-lts/releases/tag/v19.4.15
- https://github.com/OpenMage/magento-lts/releases/tag/v20.0.13
