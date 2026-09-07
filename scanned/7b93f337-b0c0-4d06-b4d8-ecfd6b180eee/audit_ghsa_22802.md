# [M] Magento Reflected cross-site scripting on customer cart page

## Summary
Severity: Medium
Advisory: GHSA-r728-jwf5-f5r5
CVE: CVE-2019-7939
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r728-jwf5-f5r5
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2

## Details
A reflected cross-site scripting vulnerability exists on the customer cart checkout page of Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2. This could be exploited by sending a victim a crafted URL that results in malicious javascript execution in the victim's browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7939
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7939.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-23
