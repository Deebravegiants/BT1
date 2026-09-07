# [M] Silverstripe XSS In FormAction

## Summary
Severity: Medium
Advisory: GHSA-4h54-vwx9-3vr3
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-4h54-vwx9-3vr3
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.0 <3.1.10

## Details
A cross-site scripting vulnerability has been discovered in the FormAction field where a user-specified title may be specified.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/1db08bac88f9330dc4e6dda1ae08628f245a5212
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-007-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/software/download/security-releases/ss-2015-007
