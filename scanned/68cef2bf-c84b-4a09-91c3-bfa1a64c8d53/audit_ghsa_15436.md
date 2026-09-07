# [H] Magento does not properly restrict excessive authentication attempts

## Summary
Severity: High
Advisory: GHSA-q628-54wg-4r5q
CVE: CVE-2024-39398
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-14
Source: https://github.com/advisories/GHSA-q628-54wg-4r5q
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p2
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p7
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p9
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p10
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4

## Details
Magento versions 2.4.7-p1, 2.4.6-p6, 2.4.5-p8, 2.4.4-p9 and earlier are affected by an Improper Restriction of Excessive Authentication Attempts vulnerability that could result in a security feature bypass. An attacker could exploit this vulnerability to perform brute force attacks and potentially gain unauthorized access to accounts. Exploitation of this issue does not require user interaction, but attack complexity is high.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39398
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb24-61.html
