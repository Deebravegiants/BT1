# [C] Magento affected by remote code execution vulnerability in the CMS page scheduled update feature

## Summary
Severity: Critical
Advisory: GHSA-4g27-q2w9-m8m8
CVE: CVE-2021-36021
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-4g27-q2w9-m8m8
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an Improper input validation vulnerability within the CMS page scheduled update feature. An authenticated attacker with administrative privilege could leverage this vulnerability to achieve remote code execution on the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36021
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
