# [C] Improper Authorization vulnerability in Magento and Adobe Commerce

## Summary
Severity: Critical
Advisory: GHSA-fppq-f2m6-xv5c
CVE: CVE-2025-24434
CWE: CWE-285, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-02-11
Source: https://github.com/advisories/GHSA-fppq-f2m6-xv5c
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.8-beta1 <2.4.8-beta2
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p4
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p9
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p11
- Packagist: `magento/community-edition` — affected >=0 <2.4.4-p12
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.8-beta1, 2.4.7-p3, 2.4.6-p8, 2.4.5-p10, 2.4.4-p11 and earlier are affected by an Improper Authorization vulnerability that could result in Privilege escalation. An attacker could leverage this vulnerability to bypass security measures and gain unauthorized access. Exploitation of this issue does not require user interaction. A successful attacker can abuse this to achieve session takeover, increasing the confidentiality and integrity impact as high.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24434
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-08.html
