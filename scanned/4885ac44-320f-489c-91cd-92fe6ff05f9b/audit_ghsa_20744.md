# [M] Magento Open Source has Improper Access Control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gm4m-9rm8-7rxj
CVE: CVE-2022-35692
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-08-20
Source: https://github.com/advisories/GHSA-gm4m-9rm8-7rxj
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.3-p1 <2.4.3-p3
- Packagist: `magento/community-edition` — affected >=2.3.7-p1 <2.3.7-p4
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected 2.4.3

## Details
Adobe Commerce versions 2.4.3-p2 (and earlier), 2.3.7-p3 (and earlier) and 2.4.4 (and earlier) are affected by an Improper Access Control vulnerability that could result in a Security feature bypass. An attacker could leverage this vulnerability to leak minor information of another user's account details. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35692
- https://helpx.adobe.com/security/products/magento/apsb22-38.html
