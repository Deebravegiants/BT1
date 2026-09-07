# [H] Budibase: Basic app users can exfiltrate stored REST datasource auth by rewriting datasource base URL

## Summary
Severity: High
Advisory: GHSA-3gp5-q4jw-3v94
CVE: CVE-2026-48152
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-3gp5-q4jw-3v94
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.39.0

## Details
### Summary
Budibase stores external REST datasource credentials server-side and documents that database credentials are applied server-side and are not exposed in the UI. The REST datasource implementation redacts stored Basic/Bearer/OAuth2 auth secrets before returning datasource data to clients. However, the single-datasource `GET` and `PUT` routes are guarded by generic `TABLE READ`, not by Builder/Admin permission or datasource-specific ownership/resource checks.

The built-in Basic app user role maps to the `WRITE` permission set, which includes table read/write and query write. A Basic user can therefore read an existing REST datasource, receive redacted `authConfigs` values, submit an update that changes only `config.url` while keeping the redacted placeholders, and trigger an existing saved relative-path REST query. During update, `mergeConfigs()` restores the old stored secret when it sees the redaction placeholder. During query execution, Budibase prefixes the attacker-controlled datasource `config.url` to the relative query path and applies the resolved stored auth headers. The result is server-side disclosure of the builder-configured REST Authorization secret to an attacker-controlled listener.

### Source evidence
- `packages/server/src/api/routes/datasource.ts`: datasource list/create/delete routes are on `builderRoutes`, but `GET /api/datasources/:datasourceId` and `PUT /api/datasources/:datasourceId` are in `authorizedRoutes` guarded only by `PermissionType.TABLE` and `PermissionLevel.READ`.
- `packages/server/src/api/routes/datasource.ts`: the `:datasourceId` routes do not attach datasource-specific resource authorization.
- `packages/backend-core/src/security/roles.ts`: built-in Basic user maps to `BuiltinPermissionID.WRITE`.
- `packages/backend-core/src/security/permissions.ts`: `WRITE` grants `READ`/`EXECUTE` levels and includes `QUERY WRITE` and `TABLE WRITE`.
- `packages/server/src/api/controllers/datasource.ts`: `datasourceController.update` reads the stored datasource, merges `ctx.request.body` into it, writes the result back, and returns a redacted copy.
- `packages/server/src/sdk/workspace/datasources/datasources.ts`: `removeSecrets()` redacts REST Basic/Bearer/OAuth2 secrets to `PASSWORD_REPLACEMENT`.
- `packages/server/src/sdk/workspace/datasources/datasources.ts`: `mergeConfigs()` restores the old stored auth-secret field when the update body sends the redaction placeholder for the same auth config.
- `packages/server/src/integrations/rest.ts`: relative REST query paths are prefixed with datasource `config.url`.
- `packages/server/src/integrations/rest.ts`: REST execution resolves the selected auth config and applies the resulting auth headers to the outbound request.
- `packages/server/src/api/routes/query.ts`: saved query execution `POST /api/v2/queries/:queryId` is guarded by `QUERY WRITE`, which the Basic role has through the `WRITE` permission set.

### Reproduction outline
No production systems were tested. This is source-backed and has a local static verifier plus a proof helper for an already-running authorized instance.

1. Deploy a current Budibase instance.
2. As a builder/admin, create and publish an app.
3. As the builder/admin, create a REST datasource with:
   - `config.url` set to a benign legitimate API base URL.
   - a stored REST auth config containing a sentinel secret, such as a Bearer token `BUDIBASE_REST_TOKEN_SENTINEL`.
4. As the builder/admin, create a saved REST query that uses a relative path and that auth config.
5. Add a non-builder Basic app user.
6. As the Basic user, confirm negative controls:
   - Builder-only datasource list/create/preview routes are denied.
   - The user is not a builder/admin.
7. As the Basic user, call `GET /api/datasources/{datasourceId}`. The response returns the datasource and redacted auth placeholders, not the raw secret.
8. As the Basic user, call `PUT /api/datasources/{datasourceId}` with the same redacted datasource body but with `config.url` changed to an attacker-controlled HTTP listener.
9. As the Basic user, execute the saved query with `POST /api/v2/queries/{queryId}`.
10. Expected vulnerable result: the attacker listener receives the server-side REST request with the preserved stored Authorization material, even though the Basic user never knew the raw secret and should not be able to administer datasource credentials.

Local source verifier:

```bash
python3 docker-proofs/s60/verify_budibase_basic_user_datasource_source_path.py
```

Expected success line:

```text
SOURCE_PATH_VERIFIED budibase_basic_user_datasource_rest_secret_exfil
```

Observed May 1, 2026:

- `origin/master` was `8e6bf89acf1f602f3334592c4c8cd14e79f5362a`.
- Latest release was `3.37.2` from Apr 30, 2026.
- The source verifier passed and confirmed the route, role, redaction, merge, URL-prefixing, auth-header, and saved-query execution conditions.

Proof-assist helper:

```bash
python3 docker-proofs/s60/proof_budibase_basic_user_datasource_update_rest_secret_exfil.py \
  --base-url http://127.0.0.1:10000 \
  --app-id <published-app-id> \
  --datasource-id <rest-datasource-id> \
  --query-id <saved-relative-rest-query-id> \
  --cookie '<basic-user-session-cookie>' \
  --expected-secret BUDIBASE_REST_TOKEN_SENTINEL
```

The helper does not start, stop, or delete containers/resources. It targets an authorized already-running instance, rewrites only `config.url`, captures the outbound Authorization material, and restores the original datasource by default.

### Impact
This breaks the intended application-user versus builder/admin boundary for external REST datasource credentials. A Basic app user should be able to use published app functionality, but should not be able to administer datasource connection settings or extract builder-configured REST auth secrets. In a realistic internal-tool deployment, REST datasource auth configs often contain bearer tokens, API keys, Basic credentials, OAuth client secrets, service account tokens, or integration credentials for ticketing, CRM, ERP, security, and operational systems.

An attacker with only Basic app-user access to an app that uses an authenticated REST datasource can redirect future query traffic to an attacker-controlled endpoint and collect the preserved server-side Authorization header. This is distinct from public REST datasource SSRF issues because the core impact is stored credential disclosure across the role boundary, and it works with an external attacker-controlled URL rather than depending on internal-network reachability.

### Remediation ideas
- Move `GET`/`PUT /api/datasources/:datasourceId` behind Builder/Admin datasource permissions, or add datasource-specific resource authorization.
- Do not allow non-builder app users to update datasource `config`, `authConfigs`, base URL, default headers, or plugin connection settings.
- Split non-sensitive datasource metadata reads from credential-bearing/admin datasource reads.
- Treat redaction placeholders as valid only in trusted builder/admin update flows.
- Consider rotating REST datasource auth secrets for affected deployments after patching.

### Duplicate/nearby public issue notes
Public triage found known Budibase REST datasource SSRF and protected-endpoint auth-bypass CVEs, but no obvious public duplicate for this specific Basic app-user `PUT /api/datasources/:id` role-boundary issue combined with preserved REST `authConfigs` secret exfiltration through a changed datasource base URL.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-3gp5-q4jw-3v94
- https://nvd.nist.gov/vuln/detail/CVE-2026-48152
- https://github.com/Budibase/budibase
