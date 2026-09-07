# [C] Silverstripe Brute force bypass on default admin

## Summary
Severity: Critical
Advisory: GHSA-8v6m-7f5v-hhx6
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-8v6m-7f5v-hhx6
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.18 <3.1.19
- Packagist: `silverstripe/framework` — affected >=3.2.3 <3.2.4
- Packagist: `silverstripe/framework` — affected >=3.3.1 <3.3.2

## Details
Default Administrator accounts were not subject to the same brute force protection afforded to other Member accounts. Failed login counts were not logged for default admins resulting in unlimited attempts on the default admin username and password.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/f32c893546340c8c279fd1ab6d4269e9d6539bc2
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-005-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2016-005
