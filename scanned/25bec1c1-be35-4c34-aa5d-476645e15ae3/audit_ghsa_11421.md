# [M] StudioCMS: REST API Missing Rank Check Allows Admin to Create Peer Admin Accounts

## Summary
Severity: Medium
Advisory: GHSA-wj56-g96r-673q
CVE: CVE-2026-32106
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-wj56-g96r-673q
Type: github-advisory

## Affected
- npm: `studiocms` — affected >=0 <0.4.3

## Details
## Summary

The REST API `createUser` endpoint uses string-based rank checks that only block creating `owner` accounts, while the Dashboard API uses `indexOf`-based rank comparison that prevents creating users at or above your own rank. This inconsistency allows an admin to create additional admin accounts via the REST API, enabling privilege proliferation and persistence.

## Details

The REST API handler in `packages/studiocms/frontend/pages/studiocms_api/_handlers/rest-api/v1/secure.ts:1365-1378`:

```typescript
// REST API — only blocks creating 'owner'
if (newUserRank === 'owner' && rank !== 'owner') {
    return yield* new RestAPIError({
        error: 'Unauthorized to create user with owner rank',
    });
}

if (rank === 'admin' && newUserRank === 'owner') {
    return yield* new RestAPIError({
        error: 'Unauthorized to create user with owner rank',
    });
}

// Missing: no check preventing admin from creating admin
// newUserRank='admin' passes all checks
```

The Dashboard API handler in `_handlers/dashboard/create.ts` uses the correct approach:

```typescript
// Dashboard API — blocks creating users at or above own rank
const callerPerm = availablePermissionRanks.indexOf(userData.permissionLevel);
const targetPerm = availablePermissionRanks.indexOf(rank);

if (targetPerm >= callerPerm) {
    return yield* new DashboardAPIError({
        error: 'Unauthorized: insufficient permissions to assign target rank',
    });
}
```

With `availablePermissionRanks = ['unknown', 'visitor', 'editor', 'admin', 'owner']`:
- Admin (index 3) creating admin (index 3): `3 >= 3` = blocked in Dashboard
- In REST API: no such check — allowed

## PoC

```bash
# 1. Use an admin-level API token

# 2. Create a new admin user via REST API
curl -X POST 'http://localhost:4321/studiocms_api/rest/v1/secure/users' \
  -H 'Authorization: Bearer <admin-api-token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "rogue_admin",
    "email": "rogue@attacker.com",
    "displayname": "Rogue Admin",
    "rank": "admin",
    "password": "StrongP@ssw0rd123"
  }'

# Expected: 403 Forbidden (admin should not create peer admin accounts)
# Actual: 200 with new admin user created
```

## Impact

- A compromised or rogue admin can create additional admin accounts as persistence mechanisms that survive password resets or token revocations
- Inconsistent security model between Dashboard API and REST API creates confusion about intended authorization boundaries
- Note: requires admin access (PR:H), which limits practical severity

## Recommended Fix

Replace string-based checks with `indexOf` comparison in `packages/studiocms/frontend/pages/studiocms_api/_handlers/rest-api/v1/secure.ts`:

```typescript
// Before:
if (newUserRank === 'owner' && rank !== 'owner') { ... }
if (rank === 'admin' && newUserRank === 'owner') { ... }

// After:
const availablePermissionRanks = ['unknown', 'visitor', 'editor', 'admin', 'owner'];
const callerPerm = availablePermissionRanks.indexOf(rank);
const targetPerm = availablePermissionRanks.indexOf(newUserRank);

if (targetPerm >= callerPerm) {
    return yield* new RestAPIError({
        error: 'Unauthorized: insufficient permissions to assign target rank',
    });
}
```

## References
- https://github.com/withstudiocms/studiocms/security/advisories/GHSA-wj56-g96r-673q
- https://nvd.nist.gov/vuln/detail/CVE-2026-32106
- https://github.com/withstudiocms/studiocms
