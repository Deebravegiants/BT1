# [H] Magento Stored Cross-Site Scripting (XSS) vulnerability 

## Summary
Severity: High
Advisory: GHSA-mmp7-8cg4-9wrg
CVE: CVE-2024-39403
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2024-08-14
Source: https://github.com/advisories/GHSA-mmp7-8cg4-9wrg
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
Magento versions 2.4.7-p1, 2.4.6-p6, 2.4.5-p8, 2.4.4-p9 and earlier are affected by a stored Cross-Site Scripting (XSS) vulnerability that could be abused by a low-privileged attacker to inject malicious scripts into vulnerable form fields. Malicious JavaScript may be executed in a victim’s browser when they browse to the page containing the vulnerable field. Confidentiality impact is high due to the attacker being able to exfiltrate sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39403
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb24-61.html
