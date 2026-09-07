# [M] Magento Open Source allows XML Injection

## Summary
Severity: Medium
Advisory: GHSA-wh42-8r2w-873x
CVE: CVE-2023-29289
CWE: CWE-91
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-15
Source: https://github.com/advisories/GHSA-wh42-8r2w-873x
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p3
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p4
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.6 (and earlier), 2.4.5-p2 (and earlier) and 2.4.4-p3 (and earlier) are affected by an XML Injection vulnerability. An attacker with low privileges can trigger a specially crafted script to a security feature bypass. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29289
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb23-35.html
