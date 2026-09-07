# [M] Magento Insecure Direct Object Reference (IDOR) in the product module

## Summary
Severity: Medium
Advisory: GHSA-8pfq-g48p-x7w8
CVE: CVE-2021-21022
CWE: CWE-285, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8pfq-g48p-x7w8
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.6-p1
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.1-p1
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento versions 2.4.1 (and earlier), 2.4.0-p1 (and earlier) and 2.3.6 (and earlier) are vulnerable to an insecure direct object reference (IDOR) in the product module. Successful exploitation could lead to unauthorized access to restricted resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21022
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-08.html
