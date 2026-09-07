# [H] Magento is affected by an os command injection via the Data collection endpoint

## Summary
Severity: High
Advisory: GHSA-qmq6-jpvg-j547
CVE: CVE-2021-36024
CWE: CWE-77, CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qmq6-jpvg-j547
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an Improper Neutralization of Special Elements Used In A Command via the Data collection endpoint. An attacker with admin privileges can upload a specially crafted file to achieve remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36024
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
