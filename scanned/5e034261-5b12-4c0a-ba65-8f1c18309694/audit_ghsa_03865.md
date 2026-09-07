# [M] Bypass of sitemp access restrictions

## Summary
Severity: Medium
Advisory: GHSA-62fx-3v4f-mwxm
CVE: CVE-2019-8133
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-11-12
Source: https://github.com/advisories/GHSA-62fx-3v4f-mwxm
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2-p2

## Details
A security bypass vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. A user with privileges to generate sitemaps can bypass configuration that restricts directory access. The bypass allows overwrite of a subset of configuration files which can lead to denial of service.

As per [the Magento Release 2.3.3](https://web.archive.org/web/20201126132230/https://devdocs.magento.com/guides/v2.3/release-notes/release-notes-2-3-3-commerce.html#new-security-only-patch-available), if you have already implemented the pre-release version of this patch (2.3.2-p1), it is highly recommended to promptly upgrade to 2.3.2-p2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8133
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8133.yaml
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
