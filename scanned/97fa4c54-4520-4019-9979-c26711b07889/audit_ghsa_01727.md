# [M] XSS injection in the Grid component of Sylius

## Summary
Severity: Medium
Advisory: GHSA-rc5r-697f-28x6
CVE: CVE-2019-12186
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-04-15
Source: https://github.com/advisories/GHSA-rc5r-697f-28x6
Type: github-advisory

## Affected
- Packagist: `sylius/grid` — affected >=1.0.0 <1.1.19
- Packagist: `sylius/grid` — affected >=1.2.0 <1.2.18
- Packagist: `sylius/grid` — affected >=1.3.0 <1.3.13
- Packagist: `sylius/grid` — affected >=1.4.0 <1.4.5
- Packagist: `sylius/grid` — affected >=1.5.0 <1.5.1
- Packagist: `sylius/grid-bundle` — affected >=1.0.0 <1.1.19
- Packagist: `sylius/grid-bundle` — affected >=1.2.0 <1.2.18
- Packagist: `sylius/grid-bundle` — affected >=1.3.0 <1.3.13
- Packagist: `sylius/grid-bundle` — affected >=1.4.0 <1.4.5
- Packagist: `sylius/grid-bundle` — affected >=1.5.0 <1.5.1
- Packagist: `sylius/sylius` — affected >=1.0.0 <1.1.18
- Packagist: `sylius/sylius` — affected >=1.2.0 <1.2.17
- Packagist: `sylius/sylius` — affected >=1.3.0 <1.3.12
- Packagist: `sylius/sylius` — affected >=1.4.0 <1.4.4

## Details
Grid component of Sylius omits HTML input sanitisation while rendering object implementing __toString() method through the string field type.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12186
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sylius/grid/CVE-2019-12186.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sylius/sylius/CVE-2019-12186.yaml
- https://sylius.com/blog/cve-2019-12186
