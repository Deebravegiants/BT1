# [M] Silverstripe XSS vulnerability via VirtualPage

## Summary
Severity: Medium
Advisory: GHSA-r97r-64vp-fghm
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-22
Source: https://github.com/advisories/GHSA-r97r-64vp-fghm
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=3.1.0 <3.1.10

## Details
A cross-site scripting vulnerability has been discovered in the VirtualPage class.

This vulnerability can only be exploited if a user with CMS access has posted malicious or unescaped HTML into any of the textfields of a page which a VirtualPage refers to.

This has been resolved by ensuring that VirtualPage safely escapes all field content.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/cms/SS-2015-005-1.yaml
- https://github.com/silverstripe/silverstripe-cms
- https://www.silverstripe.org/software/download/security-releases/ss-2015-005
