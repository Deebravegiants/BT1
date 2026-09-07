# [M] magento-lts Reset Password not protected against well-timed CSRF

## Summary
Severity: Medium
Advisory: GHSA-r3c9-9j5q-pwv4
CVE: CVE-2021-21395
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-r3c9-9j5q-pwv4
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <19.4.22
- Packagist: `openmage/magento-lts` — affected >=20.0.0 <20.0.19

## Details
### Impact

Password reset form is vulnerable to CSRF between time reset password link is clicked and user submits new password.

### Patches

PR forthcoming

### Workarounds

None

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-r3c9-9j5q-pwv4
- https://nvd.nist.gov/vuln/detail/CVE-2021-21395
- https://hackerone.com/reports/1086752
- https://github.com/OpenMage/magento-lts
- https://github.com/OpenMage/magento-lts/releases/tag/v19.4.22
- https://github.com/OpenMage/magento-lts/releases/tag/v20.0.19
- https://packagist.org/packages/openmage/magento-lts
