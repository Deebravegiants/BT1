# [H] Admidio has Inverted 2FA Reset Authorization Check that Lets Group Leaders Strip Admin TOTP

## Summary
Severity: High
Advisory: GHSA-rh3w-4ccx-prf9
CVE: CVE-2026-41660
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-rh3w-4ccx-prf9
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.9

## Details
## Summary

A logic error in Admidio's two-factor authentication reset inverts the authorization check. Non-admin users cannot remove their own TOTP configuration, but they can remove other users' TOTP, including administrators. A group leader with profile edit rights on an admin account can strip that admin's 2FA.

## Details

In `modules/profile/two_factor_authentication.php` at line 84, the authorization check uses an inverted condition:

```php
// modules/profile/two_factor_authentication.php line 84
if (!($gCurrentUser->isAdministrator() || $gCurrentUserId !== $userId))
{
    throw new AdmException('SYS_NO_RIGHTS');
}
```

By De Morgan's law, this condition evaluates as:
- Blocks when: `NOT isAdministrator() AND $gCurrentUserId === $userId`
- In practice: blocks non-admins from resetting their OWN 2FA
- Passes: non-admins resetting OTHER users' 2FA (the opposite of the intended behavior)

The intended logic should block non-admins from resetting other users' 2FA. The `!==` operator on line 84 should be `===`.

A group leader who holds `hasRightEditProfile()` permission on an admin user (checked earlier in the flow) can exploit this to strip 2FA from administrator accounts, reducing their security to password-only authentication.

## Proof of Concept

1. As `testuser` (a non-admin group leader with edit rights on admin profiles), send:

```http
POST /adm_program/modules/profile/two_factor_authentication.php HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Cookie: ADMIDIO_..._SESSION_ID=<testuser_session>

mode=reset&user_uuid=<admin_user_uuid>
```

Result: the server removes 2FA from the admin account.

2. As `testuser`, attempt to reset their own 2FA:

```http
POST /adm_program/modules/profile/two_factor_authentication.php HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Cookie: ADMIDIO_..._SESSION_ID=<testuser_session>

mode=reset&user_uuid=<testuser_user_uuid>
```

Result: `SYS_NO_RIGHTS` error. The user cannot reset their own 2FA.

This confirms the authorization logic is inverted.

## Impact

A group leader (or any user with profile edit rights on an admin) can disable two-factor authentication on administrator accounts. This degrades admin account security to password-only, opening the door to credential stuffing or brute force attacks without a 2FA barrier.

## Recommended Fix

Change `!==` to `===` on line 84 of `modules/profile/two_factor_authentication.php`:

```php
// Fixed condition: block non-admins from resetting OTHER users' 2FA
if (!($gCurrentUser->isAdministrator() || $gCurrentUserId === $userId))
{
    throw new AdmException('SYS_NO_RIGHTS');
}
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-rh3w-4ccx-prf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-41660
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.9
