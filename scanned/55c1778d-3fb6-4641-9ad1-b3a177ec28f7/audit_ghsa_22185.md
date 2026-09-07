# [H] Magento remote code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-4v2q-hjx3-c4vr
CVE: CVE-2019-8154
CWE: CWE-829
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4v2q-hjx3-c4vr
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2-p2

## Details
A remote code execution vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. An authenticated user with privileges to modify product catalogs can trigger PHP file inclusion through a crafted XML file that specifies product design update.

As per [the Magento Release 2.3.3](https://web.archive.org/web/20201126132230/https://devdocs.magento.com/guides/v2.3/release-notes/release-notes-2-3-3-commerce.html#new-security-only-patch-available), if you have already implemented the pre-release version of this patch (2.3.2-p1), it is highly recommended to promptly upgrade to 2.3.2-p2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8154
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8154.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
