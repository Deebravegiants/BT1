# [M] Magento Insecure Direct Object Reference (IDOR) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7g5j-q8qj-8984
CVE: CVE-2019-7925
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7g5j-q8qj-8984
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2

## Details
An insecure direct object reference (IDOR) vulnerability exists in Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2. This can be exploited by an administrator with limited privileges to delete the downloadable products folder.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7925
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7925.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-23
