# [M] Magento is affected by an improper authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vrq2-w7r7-3fp2
CVE: CVE-2021-36037
CWE: CWE-285, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vrq2-w7r7-3fp2
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected 2.4.2
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an improper authorization vulnerability. An authenticated attacker could leverage this vulnerability to achieve sensitive information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36037
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
