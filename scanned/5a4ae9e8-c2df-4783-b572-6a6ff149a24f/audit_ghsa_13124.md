# [C] Magento improper access control vulnerability within Magento's Media Gallery Upload workflow

## Summary
Severity: Critical
Advisory: GHSA-wqr6-wv6c-p8fx
CVE: CVE-2021-36036
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-wqr6-wv6c-p8fx
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an improper access control vulnerability within Magento's Media Gallery Upload workflow. By storing a specially crafted file in the website gallery, an authenticated attacker with administrative privilege can gain access to delete the .htaccess file. This could result in the attacker achieving remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36036
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
