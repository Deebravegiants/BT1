# [H] Magento Cross-site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-8mq8-c243-2335
CVE: CVE-2025-49557
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-8mq8-c243-2335
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.4.4-p15
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p14
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p12
- Packagist: `magento/community-edition` — affected >=2.4.7-p1 <2.4.7-p7
- Packagist: `magento/community-edition` — affected 2.4.8
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.9-alpha1, 2.4.8-p1, 2.4.7-p6, 2.4.6-p11, 2.4.5-p13, 2.4.4-p14 and earlier are affected by a stored Cross-Site Scripting (XSS) vulnerability that could be exploited by a low-privileged attacker to inject malicious scripts into vulnerable form fields. These scripts may be used to escalate privileges within the application or compromise sensitive user data. Exploitation of this issue requires user interaction in that a victim must browse to the page containing the vulnerable field. Scope is changed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49557
- https://helpx.adobe.com/security/products/magento/apsb25-71.html
