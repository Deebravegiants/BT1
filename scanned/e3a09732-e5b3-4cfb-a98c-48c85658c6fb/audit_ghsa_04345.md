# [M] NL Portal Backend Libraries: Unauthenticated form resolver forwards the privileged Objecten-API token to a caller-supplied URL (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-xm3x-9cfw-jhx4
CVE: CVE-2026-55414
CWE: CWE-862, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-xm3x-9cfw-jhx4
Type: github-advisory

## Affected
- Maven: `nl.nl-portal:form` — affected >=1.1.0 <3.0.4

## Details
## Summary

The public GraphQL resolvers `getFormDefinitionByObjectenApiUrl(url)` and the deprecated `getFormDefinitionById(id)` fetch a caller-supplied URL using the **privileged Objecten-API token**. Because the `/graphql` endpoint is `permitAll()` and these resolvers do not declare a `CommonGroundAuthentication` parameter, an **unauthenticated** caller can make the backend issue an outbound request carrying `Authorization: Token <objecten-api-token>` to a **caller-influenced URL on the configured Objecten-API host**. This is a constrained (same-host) server-side request forgery combined with missing authorization.

Reported responsibly and confirmed in a local lab build against the project's own WebFlux security stack. No production system was accessed.

## Affected

- `nl.nl-portal:form` (the public resolver / entry point) together with `nl.nl-portal:objectenapi` (where the host guard lives).
- First shipped in **1.1.0.RELEASE** (2023-10-31); the vulnerable code was introduced on 2023-08-12 (commit `b2f87ca`) and is present in every release since (1.1.x, 1.2.5, 1.3.0, the 3.0.x line, and 3.1.0 / `next-minor`, HEAD `45abcd2`). Fixed in 3.0.4.RELEASE (see Fix below).

## Data flow (confirmed in source)

1. `form/.../graphql/FormDefinitionQuery.kt` — `@QueryMapping getFormDefinitionByObjectenApiUrl(@Argument url)`, **no** `CommonGroundAuthentication` parameter (same for `getFormDefinitionById`).
2. → `form/.../service/ObjectsApiFormDefinitionService.kt` — passes the URL through unvalidated.
3. → `zgw/objectenapi/.../service/ObjectenApiService.kt` `getObjectByUrl(url)` — the only guard is host equality (`URI.create(url).host == objectsApiClientConfig.url.host`); **no scheme/port/path check**.
4. → `zgw/objectenapi/.../client/ObjectsApiClient.kt` `getObjectByUrl(url)` via `webClientWithoutBaseUrl()`, which attaches the default header `Authorization: Token <token>` to the fully caller-supplied URL.

**Reachability:** `/graphql` is `permitAll()` (`core/.../security/OauthSecurityAutoConfiguration.kt`). Authentication is only enforced on resolvers that declare a `CommonGroundAuthentication` parameter; these do not, and there is no `@PreAuthorize`/instrumentation safety net. The project's own `GraphQLEndpointAuthorizationIT` lists `getFormDefinitionByObjectenApiUrl` as an intentionally public operation — so the unauthenticated reachability is by design; the defect is that an intentionally-public resolver forwards a privileged token to a caller-influenced URL.

**Secondary (defense-in-depth):** `zgw/zaken-api/.../service/ZakenApiService.kt` `getZaakDetails` calls `objectsApiClient.getObjectByUrl` **directly**, bypassing the service-level host guard. It is currently only reachable via the authenticated `ZaakQuery.zaakdetails` field resolver with server-derived URLs, so it is not an unauthenticated vector today — but it shows why the guard belongs in the client.

## Proof of concept (lab, against the real WebFlux stack)

- An unauthenticated `POST /graphql` calling `getFormDefinitionByObjectenApiUrl(url: ...)` executes without authentication.
- With the configured Objecten-API host pointed at a mock server, an outbound request to a **caller-chosen port/path on that host** carried `Authorization: Token <configured-token>` — confirming the token is attached to caller-influenced URLs.

## Impact and severity — important limitations

Assessed as **Medium** because two code-level facts constrain practical impact:

1. **No cross-host SSRF / token exfiltration in standard deployments.** The token only travels to the *configured* Objecten-API host. Exfiltration requires an attacker-controlled listener at that host (a different port/path routing elsewhere) — generally not the case in managed deployments. A range of URL-parser bypass payloads was tested (userinfo `@`, `%2f`/`%00`/`%09`, backslash, `#`/`?`, double-host, trailing-dot, IDN/Unicode full-stop, fraction-slash, IPv6); **no parser differential** was found between the `java.net.URI`-based guard and the Spring/Netty URI builder used by WebClient — every payload either kept the request on the configured host or was rejected (fail-closed). The lab token-leak PoC works only because the configured host there is `localhost`; this does not generalize to production.

2. **Arbitrary PII object read is blocked by typed deserialization.** The response is deserialized into `ObjectsApiObject<ObjectsApiFormIoFormDefinition>`, whose envelope fields and `data.formDefinition` are all non-nullable Kotlin properties (Jackson `KotlinModule` registered). An object without a top-level `data.formDefinition` (e.g. taken/berichten/zaakdetails) fails to deserialize (`DecodingException`) and returns no data. The resolver can therefore only return objects shaped like a form definition — and form definitions are intentionally public (loaded pre-login).

**Escalation conditions** that would raise severity toward High:
- the Objecten-API host shares infrastructure with an attacker-controllable endpoint (other port/path), enabling capture of the privileged token; or
- a URL-parser differential is later found that escapes the host guard.

## Remediation

- Move the host validation out of `ObjectenApiService.getObjectByUrl` and into `ObjectsApiClient.getObjectByUrl` so the direct caller `ZakenApiService.getZaakDetails` is covered too, and tighten it from host-only to **scheme + host + port + path-prefix**. Preferably, do not accept a full URL at all: validate/extract the object UUID and rebuild the URL from the fixed configured base (reuse the existing `ObjectsApiClient.getObjectById` pattern, `/api/v2/objects/{uuid}`).
- Separately decide whether `getFormDefinitionByObjectenApiUrl` / `getFormDefinitionById` should remain unauthenticated. They are currently intentionally public (forms load before login); for a stricter posture, add a `CommonGroundAuthentication` parameter as in the other resolvers — noting this breaks pre-login form loading.

## Credit

Reported responsibly by **Ray Sabee** (https://whitehatsecurity.nl), independent security researcher — GitHub [@raysabee](https://github.com/raysabee).


## Fix

Fixed in **3.0.4.RELEASE** (commit `39ad80f`, PR #700, "rework form module"):
- The unauthenticated resolvers `getFormDefinitionByObjectenApiUrl` and the deprecated `getFormDefinitionById` were **removed** from both `FormDefinitionQuery` and the GraphQL schema.
- `getFormDefinitionByName` now requires a `CommonGroundAuthentication` parameter (no longer public).
- The URL-based service method `findObjectsApiFormDefinitionByUrl(url)` was removed and replaced by `getObjectsApiFormDefinitionById(objectId: UUID)`, which fetches by UUID via the fixed `/api/v2/objects/{uuid}` path (no caller-supplied URL, so no SSRF) and validates the object type against the configured form-definition object type.
- Form definitions are now retrieved through the new authenticated query `getFormDefinitionByTaskId(taskId)` in `nl.nl-portal:taak`, which authorizes the caller against the task (`CommonGroundAuthentication`, BSN/KVK match, else `401`) and derives the form-definition UUID from the task's own server-side data, not from caller input.
- No resolver feeds caller-controlled input into `ObjectenApiService.getObjectByUrl` anymore. The `objectenapi` module itself was not changed; the fix lives entirely in `nl.nl-portal:form` and the new `nl.nl-portal:taak` query.

## Upgrade instructions

- **Backend:** upgrade `nl.nl-portal:*` to **3.0.4** (or later).
- **Frontend:** upgrade `nl-portal-frontend-libraries` to **v3.0.3** (or later). This is required: the removed GraphQL queries (`getFormDefinitionByObjectenApiUrl`, `getFormDefinitionById`) and the now-authenticated `getFormDefinitionByName` are a breaking change. Frontend v3.0.3 uses the new authenticated `getFormDefinitionByTaskId` / `getFormDefinitionByName` queries.

## References
- https://github.com/nl-portal/nl-portal-backend-libraries/security/advisories/GHSA-xm3x-9cfw-jhx4
- https://github.com/nl-portal/nl-portal-backend-libraries/pull/700
- https://github.com/nl-portal/nl-portal-backend-libraries
