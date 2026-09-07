# [M] Silverstripe History XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6hh6-59j2-qrxw
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-22
Source: https://github.com/advisories/GHSA-6hh6-59j2-qrxw
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=3.1.0 <3.1.10

## Details
A cross-site scripting vulnerability has been discovered in the CMS page history tab.

This vulnerability can only be exploited if a user with CMS access has posted malicious or unescaped HTML into any of the text fields on a page, and if the "compare mode" option is selected. The HTML will be embedded into the page unescaped.

This has been resolved by performing the text comparison in a HTML friendly way.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/cms/SS-2015-003-1.yaml
- https://github.com/silverstripe/silverstripe-cms
- https://www.silverstripe.org/software/download/security-releases/ss-2015-003
