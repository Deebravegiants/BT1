# [M] Budibase: Missing Cache Invalidation on Public API Role Unassignment Allows Revoked Users to Retain Privileges for Up to 1 Hour

## Summary
Severity: Medium
Advisory: GHSA-6vp2-6r7m-2jvx
CVE: CVE-2026-46424
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-6vp2-6r7m-2jvx
Type: github-advisory

## Affected
- npm: `@budibase/backend-core` — affected >=0 <3.38.2

## Details
## Summary

The public API role unassignment endpoint (`POST /api/public/v1/roles/unassign`) updates user documents in CouchDB but does not invalidate the corresponding Redis user cache entries. Because the authentication middleware resolves user identity and permissions from this cache (TTL: 3600 seconds), a user whose admin, builder, or app-level roles have been revoked via the public API retains those privileges for up to 1 hour.

## Details

The root cause is an inconsistency between the `UserDB.save()` and `UserDB.bulkUpdate()` code paths.

**Vulnerable path** — `packages/pro/src/sdk/publicApi/roles.ts:49-75`:
```typescript
export async function unAssign(userIds: string[], opts: AssignmentOpts) {
  // ... modifies user objects: deletes roles, admin, builder ...
  await userDB.bulkUpdate(users)  // line 74
}
```

`bulkUpdate` delegates to `bulkUpdateGlobalUsers()` at `packages/backend-core/src/users/users.ts:82-85`:
```typescript
export async function bulkUpdateGlobalUsers(users: User[]) {
  const db = getGlobalDB()
  return (await db.bulkDocs(users)) as BulkDocsResponse
}
```

This writes directly to CouchDB with **no cache invalidation**.

**Correct path** — `packages/backend-core/src/users/db.ts:355` (used by admin UI):
```typescript
await cache.user.invalidateUser(response.id)
```

**Cache configuration** — `packages/backend-core/src/cache/user.ts:11`:
```typescript
const EXPIRY_SECONDS = 3600  // 1 hour TTL
```

**Authentication middleware** — `packages/backend-core/src/middleware/authenticated.ts:153-160`:
```typescript
user = await getUser({
  userId,
  tenantId: session.tenantId,
  email: session.email,
})
```

`getUser()` reads from Redis cache first; it only falls back to CouchDB on cache miss. After `unAssign` updates CouchDB without invalidating Redis, every authenticated request continues to use the stale cached user object with the old (revoked) privileges.

Notably, other bulk operations in the codebase handle this correctly — `groups.addUsers()` and `groups.removeUsers()` in `packages/pro/src/sdk/groups/groups.ts` both loop through affected users and call `cache.user.invalidateUser()` after `bulkUpdateGlobalUsers()`. The public API roles path was missed.

## PoC

```bash
# Prerequisites: Enterprise license, admin API key, a second user with admin role

# Step 1: Confirm user has admin access
curl -s -X GET http://localhost:10000/api/global/roles \
  -H 'Cookie: budibase:auth=<target-user-session>' \
  -H 'x-budibase-app-id: app_xyz'
# Returns 200 with roles list

# Step 2: Revoke admin role via public API
curl -s -X POST http://localhost:10000/api/public/v1/roles/unassign \
  -H 'x-budibase-api-key: <admin-api-key>' \
  -H 'Content-Type: application/json' \
  -d '{"userIds": ["<target-user-id>"], "admin": true}'
# Returns 200 — role removed from CouchDB

# Step 3: Verify DB was updated (admin field removed)
# (check CouchDB directly - user document no longer has admin: {global: true})

# Step 4: Immediately retry admin endpoint as revoked user
curl -s -X GET http://localhost:10000/api/global/roles \
  -H 'Cookie: budibase:auth=<target-user-session>' \
  -H 'x-budibase-app-id: app_xyz'
# STILL returns 200 — stale cache serves old admin privileges

# Step 5: Wait for cache expiry (up to 3600 seconds) and retry
# After cache expires, the request correctly returns 403
```

## Impact

A user whose admin, builder, or app-level roles have been revoked via the public API retains full access to those privileges for up to 1 hour. This is particularly concerning in automated offboarding scenarios where HR/IT systems use the public API to revoke access for terminated employees — the terminated user retains admin/builder access to all applications and data during the cache window.

The impact is bounded by:
- Requires enterprise license (expanded public API feature)
- Maximum 1-hour window before cache expires
- Only affects the public API revocation path; revocations via the admin UI (`UserDB.save()`) invalidate cache correctly
- The `assign` direction has the inverse issue (newly granted roles are delayed) but this is less security-critical

## Recommended Fix

Add cache invalidation to `bulkUpdateGlobalUsers` or to the callers that need it. The most targeted fix is in the `unAssign` function:

```typescript
// packages/pro/src/sdk/publicApi/roles.ts
import { cache } from "@budibase/backend-core"

export async function unAssign(userIds: string[], opts: AssignmentOpts) {
  // ... existing role removal logic ...
  await userDB.bulkUpdate(users)
  
  // Invalidate cache for all affected users
  await Promise.all(
    users.map(user => cache.user.invalidateUser(user._id!))
  )
}
```

Alternatively, fix it at the `bulkUpdate` level to prevent future callers from having the same gap:

```typescript
// packages/backend-core/src/users/db.ts
static async bulkUpdate(users: User[]) {
  const result = await usersCore.bulkUpdateGlobalUsers(users)
  await Promise.all(
    users.map(user => cache.user.invalidateUser(user._id!))
  )
  return result
}
```

The same fix should also be applied to the `assign` function in the same file.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-6vp2-6r7m-2jvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-46424
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.38.2
