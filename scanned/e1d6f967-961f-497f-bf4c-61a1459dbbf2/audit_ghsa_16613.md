# [M] silverstripe/framework Privilege Escalation Risk in Member Edit form

## Summary
Severity: Medium
Advisory: GHSA-xpff-c35g-j3cr
CWE: CWE-268
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-xpff-c35g-j3cr
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.5.7-rc1 <3.5.8
- Packagist: `silverstripe/framework` — affected >=3.6.0-rc1 <3.6.6
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.4
- Packagist: `silverstripe/framework` — affected >=4.1.0-rc1 <4.1.1

## Details
A member with the permission `EDIT_PERMISSIONS` and access to the "Security" section is able to re-assign themselves (or another member) to `ADMIN` level.

CMS Fields for the member are constructed using DirectGroups instead of Groups relation which results in bypassing security logic preventing privilege escalation.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/577138882163e4b8782ea043487944d30d88e753
- https://github.com/silverstripe/silverstripe-framework/commit/e409d6f673c49846086b23677aecdc3fde5fc4d5
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2018-001-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2018-001
