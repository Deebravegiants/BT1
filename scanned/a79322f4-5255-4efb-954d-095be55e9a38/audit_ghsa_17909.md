# [M] Magento Time-of-check Time-of-use (TOCTOU) Race Condition vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wcmw-8xpp-rwfj
CVE: CVE-2025-49558
CWE: CWE-367
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-wcmw-8xpp-rwfj
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
Magento versions 2.4.9-alpha1, 2.4.8-p1, 2.4.7-p6, 2.4.6-p11, 2.4.5-p13, 2.4.4-p14 and earlier are affected by a Time-of-check Time-of-use (TOCTOU) Race Condition vulnerability that could result in a security feature bypass. An attacker could exploit this vulnerability by manipulating the timing between the check of a resource's state and its use, allowing unauthorized write access. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49558
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-71.html
