# [M] Magento Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-273r-v888-vgc6
CVE: CVE-2019-8153
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-273r-v888-vgc6
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2-p2

## Details
A mitigation bypass to prevent cross-site scripting (XSS) exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. Successful exploitation of this vulnerability would result in an attacker being able to bypass the `escapeURL()` function and execute a malicious XSS payload.

As per [the Magento Release 2.3.3](https://web.archive.org/web/20201126132230/https://devdocs.magento.com/guides/v2.3/release-notes/release-notes-2-3-3-commerce.html#new-security-only-patch-available), if you have already implemented the pre-release version of this patch (2.3.2-p1), it is highly recommended to promptly upgrade to 2.3.2-p2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8153
- https://github.com/magento/magento2/commit/c6ab7ac38f25309318e5819d4bdd936b2a0cf6bd
- https://github.com/magento/magento2/commit/f5eb758c12a2c40ba3fe38ce44b46192494f4ff8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8153.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
