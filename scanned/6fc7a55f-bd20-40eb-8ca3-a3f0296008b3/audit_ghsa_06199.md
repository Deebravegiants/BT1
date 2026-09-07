# [M] Laravel Backpack CRUD: MyAccountController allows changing the login email without a current-password check

## Summary
Severity: Medium
Advisory: GHSA-9fw9-8c49-qch8
CVE: CVE-2026-54176
CWE: CWE-287, CWE-620
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-9fw9-8c49-qch8
Type: github-advisory

## Affected
- Packagist: `backpack/crud` — affected >=6.0.0 <6.8.14
- Packagist: `backpack/crud` — affected >=7.0.0 <7.0.38

## Details
## Summary

`MyAccountController::postAccountInfoForm` allows an authenticated user to update
the authentication column (default: `email`) without verifying their current password.
Because email is the account-recovery anchor, this enables account takeover after
the attacker's session ends: the new email address can be used to request a password
reset from outside the system.

The password-change endpoint in the same controller correctly requires `old_password`
verification, so the gap is asymmetric.

## Details

The `postAccountInfoForm` action passes `$request->validated()` directly to
`$user->update()`. The `AccountInfoRequest` whitelists the authentication column
(`email` by default) with no ownership challenge. Contrast this with
`ChangePasswordRequest`, which uses `Hash::check` against the stored password before
allowing any change.

Scenarios where this is exploitable include:
- A brief unauthorized session (e.g. unattended workstation, XSS in the admin panel)
- An insider/offboarding case where a departing admin sets a personal email address
  before access is revoked, then resets the password after leaving

## Patch

Fixed in [#5990](https://github.com/Laravel-Backpack/CRUD/pull/5990) — the
authentication column is now protected by a `current_password` check (mirroring
`ChangePasswordRequest`) whenever its value changes.

A stronger mitigation — sending a verification link to the new address before
persisting the change — can be layered on top using Laravel's `MustVerifyEmail` flow.

## Affected versions

All versions prior to 6.8.14 / 7.0.38.

## Fixed versions

- 6.x: 6.8.14
- 7.x: 7.0.38

## References
- https://github.com/Laravel-Backpack/CRUD/security/advisories/GHSA-9fw9-8c49-qch8
- https://github.com/Laravel-Backpack/CRUD/pull/5990
- https://github.com/Laravel-Backpack/CRUD
- https://github.com/Laravel-Backpack/CRUD/releases/tag/6.8.14
- https://github.com/Laravel-Backpack/CRUD/releases/tag/7.0.38
