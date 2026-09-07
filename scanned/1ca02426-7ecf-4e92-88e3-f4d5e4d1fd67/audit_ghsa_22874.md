# [C] Magento executes code via the API File Option Upload Extension

## Summary
Severity: Critical
Advisory: GHSA-6cwv-wj7v-73xp
CVE: CVE-2021-36042
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6cwv-wj7v-73xp
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected 2.4.2
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an improper input validation vulnerability in the API File Option Upload Extension. An attacker with Admin privileges can achieve unrestricted file upload which can result in remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36042
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
