# [C] Magento has a  file extension restrictions bypass

## Summary
Severity: Critical
Advisory: GHSA-2pq5-gpqf-g4r3
CVE: CVE-2021-36040
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2pq5-gpqf-g4r3
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected 2.4.2
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an improper input validation vulnerability. An attacker with admin privileges can upload a specially crafted file to bypass file extension restrictions and could lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36040
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
