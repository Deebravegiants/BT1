# [H] @actual-app/sync-server: Disabled OpenID users keep access through existing session tokens

## Summary
Severity: High
Advisory: GHSA-cq9c-6w48-qmfg
CVE: CVE-2026-49229
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-cq9c-6w48-qmfg
Type: github-advisory

## Affected
- npm: `@actual-app/sync-server` — affected >=0 <26.6.0

## Details
### Summary

In OpenID multi-user mode, disabling a user only blocks future OpenID login for that identity. Existing Actual session tokens for the disabled user remain valid, so the user can continue calling authenticated server endpoints after an administrator has disabled the account.

### Details

The disabled-user check is present during OpenID login finalization. Existing users are only accepted when the matching row has `enabled = 1`, and a disabled row causes the OpenID grant to fail before a new session token is created.

```ts
// packages/sync-server/src/accounts/openid.ts:284-291
const { id: userIdFromDb, display_name: displayName } =
  accountDb.first(
    'SELECT id, display_name FROM users WHERE user_name = ? and enabled = 1',
    [identity],
  ) || {};

if (userIdFromDb == null) {
  throw new Error('openid-grant-failed');
}
```

The shared session validation path does not perform the same enabled-user check. It accepts any existing token row that has not expired, then returns the session object to every route protected by `validateSessionMiddleware`.

```ts
// packages/sync-server/src/util/validate-user.ts:10-41
export function validateSession(req: Request, res: Response) {
  let { token } = req.body || {};
  if (!token) {
    token = req.headers['x-actual-token'];
  }

  const session = getSession(token);
  ...
  return session;
}
```

This means account disablement and session authorization diverge:

```text
OpenID login path: users.enabled must be 1
Existing session path: token exists and is not expired; users.enabled is not checked
```

The default token expiration setting is `never`, so this is not just a short race after disablement on default deployments.

```js
// packages/sync-server/src/load-config.js:260-264
token_expiration: {
  doc: 'Token expiration time.',
  format: 'tokenExpiration',
  default: 'never',
  env: 'ACTUAL_TOKEN_EXPIRATION',
},
```

Admins can change a user's enabled state through the user update route, but that update does not delete the user's existing sessions. After the update, the old token still satisfies `validateSession`.

```js
// packages/sync-server/src/app-admin.js:91-101
app.patch('/users', validateSessionMiddleware, async (req, res) => {
  if (!isAdmin(res.locals.user_id)) {
    ...
  }

  const { id, userName, role, displayName, enabled } = req.body || {};
```

```ts
// packages/sync-server/src/services/user-service.ts:98-102
getAccountDb().mutate(
  'UPDATE users SET user_name = ?, display_name = ?, enabled = ?, role = ? WHERE id = ?',
  [userName, displayName, enabled, roleId, userId],
);
```

Authenticated server features then continue to trust that session. For example, the sync API installs `validateSessionMiddleware` for the whole router, so a disabled user can keep using any sync operation that their still-valid session and existing file ownership/access allow.

```ts
// packages/sync-server/src/app-sync.ts:37-39
const app = express();
app.use(validateSessionMiddleware);
app.use(errorMiddleware);
```

This is distinct from the previously published cross-user sync authorization issue: the attacker does not need to access another user's file ID. The bypass is that a disabled user's own session remains authorized after account disablement.

### PoC

1. Run an Actual Sync Server in OpenID multi-user mode with `@actual-app/sync-server` 26.5.0. Use the default token expiration setting, or any setting where the token has not expired yet.
2. Log in as a non-admin OpenID user and save the returned Actual session token.
3. As an admin, disable that same user through `PATCH /admin/users` by sending `enabled: false`.
4. Reuse the old token against a protected endpoint.

Example success check:

```bash
curl -s https://actual.example.com/account/validate \
  -H 'X-Actual-Token: <disabled_user_existing_token>'
```

Expected result on the affected code path: the request is still treated as authenticated and returns the disabled user's account/session information instead of `401` or `403`.

A sync-facing check uses the same session validation primitive:

```bash
curl -s https://actual.example.com/sync/list-user-files \
  -H 'X-Actual-Token: <disabled_user_existing_token>'
```

Expected result on the affected code path: the disabled user can still list and operate on budget files that the stale session is otherwise allowed to access.

### Impact

A disabled OpenID user can keep post-authentication access until the session row is deleted or expires. With the default `token_expiration: never`, this can persist indefinitely.

For a disabled basic user, the confirmed impact is continued access to that user's own budgets and any budgets shared with that user, including sensitive financial data and allowed mutations. For a disabled admin user, the impact is broader because the existing token can still satisfy admin role checks; that condition preserves administrative access after the account was disabled.

The missing rule is that session validation should reject disabled users, and disabling or deleting a user should revoke that user's existing sessions.

## References
- https://github.com/actualbudget/actual/security/advisories/GHSA-cq9c-6w48-qmfg
- https://github.com/actualbudget/actual
