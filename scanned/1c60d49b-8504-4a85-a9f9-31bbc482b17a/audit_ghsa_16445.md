# [M] silverstripe/framework has Cross-site Scripting vulnerability in CMSSecurity BackURL

## Summary
Severity: Medium
Advisory: GHSA-r85g-7jpv-8xrx
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-r85g-7jpv-8xrx
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.0-rc1 <3.1.21
- Packagist: `silverstripe/framework` — affected >=3.2.0-rc1 <3.2.6
- Packagist: `silverstripe/framework` — affected >=3.3.0-rc1 <3.3.4
- Packagist: `silverstripe/framework` — affected >=3.4.0-rc1 <3.4.2

## Details
In follow up to [SS-2016-001](https://www.silverstripe.org/download/security-releases/ss-2016-001/) there is yet a minor unresolved fix to incorrectly encoded URL.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/6b123fe1c93d3ac976f484192abc31cad4f81d47
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-016-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2016-016
