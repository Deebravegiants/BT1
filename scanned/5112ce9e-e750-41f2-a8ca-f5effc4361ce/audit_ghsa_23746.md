# [C] Magento has an XML Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-5pjj-7fq8-9gpf
CVE: CVE-2021-36028
CWE: CWE-91
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5pjj-7fq8-9gpf
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an XML Injection vulnerability when saving a configurable product. An attacker with admin privileges can trigger a specially crafted script to achieve remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36028
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
