# [M] Silverstripe XSS In GridField print

## Summary
Severity: Medium
Advisory: GHSA-88jp-9jrv-6368
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-88jp-9jrv-6368
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.0 <3.1.10

## Details
A cross-site scripting vulnerability has been discovered in the print view of  GridField.

This vulnerability can only be exploited if a user with CMS access has posted malicious or unescaped HTML into any field of an object in a GridField, and the print feature is used.

This has been resolved by ensuring that the print feature safely escapes all fields.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/cebc0d08c5cc8177c2462a963b76e5bc7827146d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-006-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/software/download/security-releases/ss-2015-006
