# [M] Magento Insufficient authorization check when adding users to company accounts

## Summary
Severity: Medium
Advisory: GHSA-pfxv-66r9-4gqw
CVE: CVE-2019-7872
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pfxv-66r9-4gqw
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2

## Details
An insecure direct object reference (IDOR) vulnerability exists in Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2 due to insufficient authorizations checks. This can be abused by a user with admin privileges to add users to company accounts or modify existing user details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7872
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7872.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
