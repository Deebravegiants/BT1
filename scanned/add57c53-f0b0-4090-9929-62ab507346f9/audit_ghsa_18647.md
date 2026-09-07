# [H] Magento vulnerable to stored Cross-Site Scripting (XSS)

## Summary
Severity: High
Advisory: GHSA-2768-5wmv-cfff
CVE: CVE-2025-54264
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-14
Source: https://github.com/advisories/GHSA-2768-5wmv-cfff
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=2.4.9-alpha1 <2.4.9-alpha3
- Packagist: `magento/community-edition` — affected >=2.4.8-beta1 <2.4.8-p3
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p8
- Packagist: `magento/community-edition` — affected >=0 <2.4.6-p13
- Packagist: `magento/community-edition` — affected 2.4.8
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6

## Details
Magento versions 2.4.9-alpha2, 2.4.8-p2, 2.4.7-p7, 2.4.6-p12, 2.4.5-p14, 2.4.4-p15 and earlier are affected by a stored Cross-Site Scripting (XSS) vulnerability that could be abused by a high-privileged attacker to inject malicious scripts into vulnerable form fields. Malicious JavaScript may be executed in a victim’s browser when they browse to the page containing the vulnerable field. A successful attacker can abuse this to achieve session takeover, increasing the confidentiality, and integrity impact to high. Exploitation of this issue requires user interaction in that a victim must browse to the page containing the vulnerable field. Scope is changed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54264
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-94.html
