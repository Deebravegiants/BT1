# [H] Magento Path Traversal vulnerability via the `theme[preview_image]` parameter

## Summary
Severity: High
Advisory: GHSA-7w95-qwhh-q9p3
CVE: CVE-2021-36031
CWE: CWE-22
Ecosystem: Packagist
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7w95-qwhh-q9p3
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by a Path Traversal vulnerability via the `theme[preview_image]` parameter. An attacker with admin privileges could leverage this vulnerability to achieve remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36031
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
