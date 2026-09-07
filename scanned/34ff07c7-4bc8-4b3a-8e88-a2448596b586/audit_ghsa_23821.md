# [M] Magento affected by a business logic error in the placeOrder graphql mutation

## Summary
Severity: Medium
Advisory: GHSA-3f97-7pgv-gmgr
CVE: CVE-2021-36012
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3f97-7pgv-gmgr
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by a business logic error in the placeOrder graphql mutation. An authenticated attacker can leverage this vulnerability to altar the price of an item.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36012
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
