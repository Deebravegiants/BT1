# [C] Magneto contains stored XSS vulnerability

## Summary
Severity: Critical
Advisory: GHSA-j934-vjh5-vf9r
CVE: CVE-2025-47110
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-j934-vjh5-vf9r
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.8-beta1 <2.4.8-p1
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p6
- Packagist: `magento/community-edition` — affected >=0 <2.4.5-p13
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.8
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p11
- Packagist: `magento/community-edition` — affected 2.4.6

## Details
Magento versions 2.4.8, 2.4.7-p5, 2.4.6-p10, 2.4.5-p12, 2.4.4-p13 and earlier are affected by a stored Cross-Site Scripting (XSS) vulnerability that could be abused by a high privileged attacker to inject malicious scripts into vulnerable form fields. Malicious JavaScript may be executed in a victim’s browser when they browse to the page containing the vulnerable field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47110
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-50.html
