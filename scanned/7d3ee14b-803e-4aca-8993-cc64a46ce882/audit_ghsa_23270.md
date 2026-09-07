# [H] Magento 2 Community Unrestricted File Upload

## Summary
Severity: High
Advisory: GHSA-3h69-4frw-g2jm
CVE: CVE-2019-7930
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3h69-4frw-g2jm
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2

## Details
A file upload restriction bypass exists in Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2. An authenticated user with administrator privileges to the import feature can make modifications to a configuration file, resulting in potentially unauthorized removal of file upload restrictions. This can result in arbitrary code execution when a malicious file is then uploaded and executed on the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7930
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7930.yaml
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
- https://web.archive.org/web/20211206084839/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
