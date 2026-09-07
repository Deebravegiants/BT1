# [M] silverstripe/framework ChangePasswordForm does not check `Member::canLogIn()`

## Summary
Severity: Medium
Advisory: GHSA-p5h2-vr99-xm99
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-p5h2-vr99-xm99
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.19-rc1 <3.1.20
- Packagist: `silverstripe/framework` — affected >=3.2.4-rc1 <3.2.5
- Packagist: `silverstripe/framework` — affected >=3.3.2-rc1 <3.3.3
- Packagist: `silverstripe/framework` — affected >=3.4.0-rc1 <3.4.1

## Details
After performing a password reset, `ChangePasswordForm::doChangePassword()` logs in the user without checking `Member::canLogIn()`. This presents an issue for sites that are using the extension point in that method to deny access to users (for example members that have not been “approved”, or members that have had their access revoked temporarily). It looks like `Member::canLogIn()` was originally designed to only be used for checking whether the user is locked out (due to too many incorrect login attempts) but has been opened up to other uses.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/2b30ade44d333a4da4d13b31ffa28d0a34597442
- https://github.com/silverstripe/silverstripe-framework/commit/6606d986634f5b5dec16462acaa8d9a513c29fec
- https://github.com/silverstripe/silverstripe-framework/commit/6d41db77fa78f473db7bcff389456c980ef4e412
- https://github.com/silverstripe/silverstripe-framework/commit/782c18fd13b9fb92707d0ea3b231023204928297
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-011-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2016-011
