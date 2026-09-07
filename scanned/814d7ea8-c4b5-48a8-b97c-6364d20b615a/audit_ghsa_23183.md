# [M] Magento Improper Authorization vulnerability in the customers module

## Summary
Severity: Medium
Advisory: GHSA-cc3w-r3w8-hfh7
CVE: CVE-2021-28567
CWE: CWE-285, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cc3w-r3w8-hfh7
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.2-p1
- Packagist: `magento/community-edition` — affected >=0 <2.3.7
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento versions 2.4.2 (and earlier), 2.4.1-p1 (and earlier) and 2.3.6-p1 (and earlier) are vulnerable to an Improper Authorization vulnerability in the customers module. Successful exploitation could allow a low-privileged user to modify customer data. Access to the admin console is required for successful exploitation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28567
- https://github.com/magento/magento2/commit/1bd5cb8c065e44779526c0b044ce19b884707695
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-30.html
