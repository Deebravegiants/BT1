# [H] Magento DOM-based Cross-Site Scripting (XSS) vulnerability

## Summary
Severity: High
Advisory: GHSA-52fg-wjxm-pp44
CVE: CVE-2024-39400
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-14
Source: https://github.com/advisories/GHSA-52fg-wjxm-pp44
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p2
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p7
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p9
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p10
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4

## Details
Magento versions 2.4.7-p1, 2.4.6-p6, 2.4.5-p8, 2.4.4-p9 and earlier are affected by a DOM-based Cross-Site Scripting (XSS) vulnerability. This vulnerability could allow an admin attacker to inject and execute arbitrary JavaScript code within the context of the user's browser session. Exploitation of this issue requires user interaction, such as convincing a victim to click on a malicious link. Confidentiality and integrity impact is high as it affects other admin accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39400
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb24-61.html
