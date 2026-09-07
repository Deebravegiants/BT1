# [H] Craft CMS: Arbitrary user password reset leading to administrator account takeover

## Summary
Severity: High
Advisory: GHSA-p8x7-9vfw-p7vc
CWE: CWE-285
Ecosystem: Packagist
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-p8x7-9vfw-p7vc
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.10.8

## Details
The vulnerability allows any authenticated user to change their own password without providing the current password or having an active elevated session. It also allows the attacker to change other users’ passwords if the attacker’s account has `edit users` permission (which doesn’t allow changing others’ passwords) and lacks `Administrate users` permission (which is required to change others’ passwords).

The vulnerability exists in the `elements/save` action when saving a User element. The `UserPasswordValidator` applies only a `safe` validator to the `newPassword` field without an `on` scenario restriction. This makes `newPassword` mass-assignable during the generic element save flow, completely bypassing the dedicated `users/set-password` action that enforces elevated session verification.

An attacker with any authenticated session (whether it’s hijacked or a normal / low-privileged user) can change their own password, and potentially take over administrator accounts.

## Required Permissions
- Access the control panel
- Edit users (needed for the account takeover attack scenario)

## Impact
- Any authenticated user can change their own password without providing their current password.
- Users with Edit users permission can change any user’s password, including administrators.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-p8x7-9vfw-p7vc
- https://github.com/craftcms/cms/commit/cbdf45fbd3ab548b147d7de375f6f6f580b7c294
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/5.10.8
