# [M] Magento Open Source allows Information Exposure

## Summary
Severity: Medium
Advisory: GHSA-85m4-g9vq-xpxj
CVE: CVE-2023-29287
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-06-15
Source: https://github.com/advisories/GHSA-85m4-g9vq-xpxj
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p3
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p4
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.6 (and earlier), 2.4.5-p2 (and earlier) and 2.4.4-p3 (and earlier) are affected by an Information Exposure vulnerability that could lead to a security feature bypass. An attacker could leverage this vulnerability to leak minor user data. Exploitation of this issue does not require user interaction..

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29287
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb23-35.html
