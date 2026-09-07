# [H] Magento Cross-Site Request Forgery (CSRF) vulnerability

## Summary
Severity: High
Advisory: GHSA-5777-jj7p-mpqw
CVE: CVE-2025-49555
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-5777-jj7p-mpqw
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=2.4.9-alpha1 <2.4.9-alpha2
- Packagist: `magento/community-edition` — affected >=2.4.8-beta1 <2.4.8-p2
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p7
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p12
- Packagist: `magento/community-edition` — affected >=0 <2.4.5-p14
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.8

## Details
Magento versions 2.4.9-alpha1, 2.4.8-p1, 2.4.7-p6, 2.4.6-p11, 2.4.5-p13, 2.4.4-p14 and earlier are affected by a Cross-Site Request Forgery (CSRF) vulnerability that could result in privilege escalation. A high-privileged attacker could trick a victim into executing unintended actions on a web application where the victim is authenticated, potentially allowing unauthorized access or modification of sensitive data. Exploitation of this issue requires user interaction in that a victim must visit a malicious website or click on a crafted link. Scope is changed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49555
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-71.html
