# [M] silverstripe/framework vulnerable to member disclosure in login form

## Summary
Severity: Medium
Advisory: GHSA-crr3-h4m8-7f56
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-crr3-h4m8-7f56
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.4
- Packagist: `silverstripe/framework` — affected >=4.1.0-rc1 <4.1.1

## Details
There is a user ID enumeration vulnerability in our brute force error messages.

- Users that don't exist in will never get a locked out message
- Users that do exist, will get a locked out message

This means an attacker can infer or confirm user details that exist in the member table.

This issue has been resolved by ensuring that login attempt logging and lockout process works equivalently for non-existent users as it does for existant users.

This is a regression of [SS-2017-002](https://www.silverstripe.org/download/security-releases/ss-2017-002).

## References
- https://github.com/silverstripe/silverstripe-framework/commit/5887201dd578a5b9779c33a182153d2ce973ab41
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2018-010-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2018-010
