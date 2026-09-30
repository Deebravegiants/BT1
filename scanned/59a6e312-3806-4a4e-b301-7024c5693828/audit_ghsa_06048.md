# [H] Snipe-IT has an Improper Privilege Management issue

## Summary
Severity: High
Advisory: GHSA-j5g3-42wp-gqm3
CVE: CVE-2026-55843
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-j5g3-42wp-gqm3
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.0

## Details
## Impact

The `update()` method in `UsersController` passes the `permission` request field unconditionally to `NormalizePermissionsPayloadAction`, which returns an empty array when the field is absent. The result is passed to `PreserveUnauthorizedPrivilegedPermissionsAction`, which selectively restores only the `superuser` key (when the editor is not a superuser) and the `admin` key (when the editor is neither admin nor superuser). All other permissions — including the `admin` flag itself when the editing user is an admin — are discarded and `$user->permissions` is overwritten with the sparse result.

The `canEditAuthFields` gate permits admins to update other non-superuser accounts (including other admins). When an admin sends a `PUT /users/{id}` request for another admin without including the `permission` field, the target's `admin` flag and all granular permissions are permanently destroyed. The target loses administrative access entirely with no error, warning, or out-of-band notification.

A secondary, lower-impact path exists for non-admin users holding the `users.edit` permission: they may target regular (non-admin, non-superuser) accounts and wipe all granular permissions in the same way.

### Patches
Patched in https://github.com/grokability/snipe-it/commit/1cff2d67aabd00ee51d864c1d7fb717494c1d6ad

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-j5g3-42wp-gqm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-55843
- https://github.com/grokability/snipe-it/commit/1cff2d67aabd00ee51d864c1d7fb717494c1d6ad
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.0
