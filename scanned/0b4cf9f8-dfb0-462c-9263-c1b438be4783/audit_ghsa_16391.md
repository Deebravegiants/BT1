# [M] Magento Open Source allows Cross-Site Request Forgery (CSRF)

## Summary
Severity: Medium
Advisory: GHSA-hqgj-4396-hmxv
CVE: CVE-2024-20718
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-02-15
Source: https://github.com/advisories/GHSA-hqgj-4396-hmxv
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p4
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p6
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p7
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.6-p3, 2.4.5-p5, 2.4.4-p6 and earlier are affected by a Cross-Site Request Forgery (CSRF) vulnerability that could result in a Security feature bypass. An attacker could leverage this vulnerability to trick a victim into performing actions they did not intend to do, which could be used to bypass security measures and gain unauthorized access. Exploitation of this issue requires user interaction, typically in the form of the victim clicking a link or visiting a malicious website.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-20718
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb24-03.html
