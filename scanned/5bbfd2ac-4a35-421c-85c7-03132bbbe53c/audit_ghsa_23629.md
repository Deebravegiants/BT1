# [M] Magento 2 Community Edition Path Disclosure

## Summary
Severity: Medium
Advisory: GHSA-xcgp-c6hp-cj4r
CVE: CVE-2019-7852
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xcgp-c6hp-cj4r
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2

## Details
A path disclosure vulnerability exists in Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2. Requests for a specific file path could result in a redirect to the URL of the Magento admin panel, disclosing its location to potentially unauthorized parties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7852
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7852.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-33
- https://web.archive.org/web/20220121011306/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-33
