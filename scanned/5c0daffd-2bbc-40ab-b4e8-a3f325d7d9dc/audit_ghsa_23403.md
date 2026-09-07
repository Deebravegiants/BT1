# [H] Magento affected by remote code execution via a file upload

## Summary
Severity: High
Advisory: GHSA-j46h-qjjv-cxfj
CVE: CVE-2021-36034
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j46h-qjjv-cxfj
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected 2.4.2
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an improper input validation vulnerability. An attacker with admin privileges can upload a specially crafted file to achieve remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36034
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
