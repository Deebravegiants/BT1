# [H] Magento has incorrect authorization issue that leads to arbitrary file system read

## Summary
Severity: High
Advisory: GHSA-7hrj-3c9x-xv5h
CVE: CVE-2025-49556
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-7hrj-3c9x-xv5h
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=2.4.9-alpha1 <2.4.9-alpha2
- Packagist: `magento/community-edition` — affected >=2.4.8-beta1 <2.4.8-p2
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p7
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p12
- Packagist: `magento/community-edition` — affected >=0 <2.4.5-p14
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.8

## Details
Magento versions 2.4.9-alpha1, 2.4.8-p1, 2.4.7-p6, 2.4.6-p11, 2.4.5-p13, 2.4.4-p14 and earlier are affected by an Incorrect Authorization vulnerability that could result in a security feature bypass. An attacker could leverage this vulnerability to bypass security measures and gain unauthorized read access. Exploitation of this issue does not require user interaction, and scope is unchanged.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49556
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-71.html
