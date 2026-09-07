# [M] Silverstripe Missing security check on dev/build/defaults

## Summary
Severity: Medium
Advisory: GHSA-x5w2-wcr8-9q45
CWE: CWE-425
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-x5w2-wcr8-9q45
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <3.1.17
- Packagist: `silverstripe/framework` — affected >=3.2.0 <3.2.2
- Packagist: `silverstripe/framework` — affected >=3.3.0-beta1 <3.3.0

## Details
The buildDefaults method on DevelopmentAdmin is missing a permission check.

In live mode, if you access /dev/build, you are requested to login first. However, if you access /dev/build/defaults, then the action is performed without any login check. This should be protected in the same way that /dev/build is.
The buildDefaults view is requireDefaultRecords() on each DataObject class, and hence has the potential to modify database state. It also lists all modified tables, allowing attackers more insight into which modules are used, and how the database tables are structured.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/15d4db3b4a7dbc9a7e089f9329a396f8408ed7d9
- https://github.com/silverstripe/silverstripe-framework/commit/3398f670d881447f8777b567f1ead7c0d8d253f5
- https://github.com/silverstripe/silverstripe-framework/commit/5d2fc0d7cac4ce686f7ae05c1a7b1ad8c01711a8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-028-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2015-028
