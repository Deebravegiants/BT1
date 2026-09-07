# [H] Magento 2 Community Edition Access Control Bypass

## Summary
Severity: High
Advisory: GHSA-2fhr-f6q6-c4p2
CVE: CVE-2019-7950
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2fhr-f6q6-c4p2
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2

## Details
An access control bypass vulnerability exists in Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2. An unauthenticated user can bypass access controls via REST API calls to assign themselves to an arbitrary company, thereby gaining read access to potentially confidental information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7950
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7950.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
- https://web.archive.org/web/20211206084839/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
