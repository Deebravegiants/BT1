# [M] Information disclosure through processing of external XML entities

## Summary
Severity: Medium
Advisory: GHSA-427g-2r83-3ccm
CVE: CVE-2019-8126
CWE: CWE-611, CWE-776
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-11-12
Source: https://github.com/advisories/GHSA-427g-2r83-3ccm
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2-p2

## Details
An XML entity injection vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. An authenticated admin user can craft document type definition for an XML representing XML layout. The crafted document type definition and XML layout allow processing of external entities which can lead to information disclosure.

As per [the Magento Release 2.3.3](https://web.archive.org/web/20201126132230/https://devdocs.magento.com/guides/v2.3/release-notes/release-notes-2-3-3-commerce.html#new-security-only-patch-available), if you have already implemented the pre-release version of this patch (2.3.2-p1), it is highly recommended to promptly upgrade to 2.3.2-p2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8126
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8126.yaml
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
