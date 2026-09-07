# [H] Traefik: Incomplete fix for CVE-2026-33433 + CVE-2026-39858 cross-cohort: headerField underscore-variant identity spoofing in BasicAuth / DigestAuth / ForwardAuth

## Summary
Severity: High
Advisory: GHSA-x677-9fxg-v5c5
CVE: CVE-2026-54763
CWE: CWE-178, CWE-290, CWE-345
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-x677-9fxg-v5c5
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.51
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.22
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0 <3.7.6

## Details
## Summary

There is a high severity vulnerability in Traefik's BasicAuth, DigestAuth, and ForwardAuth
middlewares. The fix for CVE-2026-33433 stripped canonical-cased spoofed identity headers
(e.g. `X-Auth-User`) before writing Traefik's own value, but did not account for
underscore-variant header names (e.g. `X_Auth_User`), which many backends normalize
identically to the dashed form. An attacker able to reach a protected route could inject
an underscore-variant header that survives Traefik's stripping and reaches the backend
alongside — or, on the unauthenticated ForwardAuth `authResponseHeaders` path, instead of
— the value Traefik intended to set, spoofing identity or authorization context. This is
fixed by setting the new `allowHeadersWithUnderscores: false` entry point option, which
strips all headers with underscores in their names before routing.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.51
- https://github.com/traefik/traefik/releases/tag/v3.6.22
- https://github.com/traefik/traefik/releases/tag/v3.7.6

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

# Incomplete fix for CVE-2026-33433 + CVE-2026-39858 cross-cohort: `headerField` underscore-variant identity spoofing in BasicAuth / DigestAuth / ForwardAuth

## Summary

The fix for CVE-2026-33433 (GHSA-qr99-7898-vr7c, "BasicAuth/DigestAuth Identity Spoofing via Non-Canonical headerField", patched in v2.11.42 / v3.6.12 / v3.7.0-ea.3) added `req.Header.Del(headerField)` before the literal-key writeback in `pkg/middlewares/auth/basic_auth.go` and `pkg/middlewares/auth/digest_auth.go`. Go's `Header.Del` calls `textproto.CanonicalMIMEHeaderKey` which canonicalizes ASCII CASE and treats `-` as a word separator — so the fix correctly strips canonical-cased attacker headers (`X-Auth-User`, `x-auth-user`, `X-AUTH-USER`, etc.).

However, `textproto.CanonicalMIMEHeaderKey` does **NOT** treat `_` as a separator. Attacker-supplied **underscore-variant** headers such as `X_Auth_User` survive `Header.Del("X-Auth-User")` intact and are forwarded to the backend alongside Traefik's own writeback. Many common backends (CGI/WSGI per RFC 3875, PHP `$_SERVER`, nginx with `underscores_in_headers on`, Tomcat / Java EE servlet containers, ASGI/WSGI frameworks) normalize `_` ↔ `-` equivalently or expose both forms to application code that may read the attacker's value.

This is the **direct cross-cohort sibling** of the threat model the maintainer accepted in **CVE-2026-39858** (GHSA-5m6w-wvh7-57vm, "Forwarded alias spoofing pre-auth decision bypass"), which fixed the underscore-variant of the X-Forwarded-* family via `isManagedXHeader` in `pkg/middlewares/forwardedheaders/forwarded_header.go`. The CVE-2026-39858 advisory body states verbatim:

> "When the backend normalizes underscore and dash header forms equivalently, an attacker can inject spoofed trust context — such as a trusted scheme or host — through the alias headers and bypass authentication on protected routes without valid credentials."

The same threat model applies to the operator-configurable `headerField` (BasicAuth, DigestAuth) and `authResponseHeaders` (ForwardAuth, ingress-nginx snippet provider), but the underscore-handling primitive (`isManagedXHeader`) was not extended to those middlewares. I verified the bypass end-to-end on `traefik:v3.6.14` (the latest patched release containing both fixes) using a default-recommended canonical `headerField: "X-Auth-User"` config and reproduced the bypass with a single `curl -H "X_Auth_User: superadmin" ...` request alongside valid BasicAuth credentials.

The defect is present in four code paths at HEAD `eec68dce064f843b4317c4393aaea81b6dea31d6`:

1. `pkg/middlewares/auth/basic_auth.go:101-105` — BasicAuth `headerField`
2. `pkg/middlewares/auth/digest_auth.go:99-103` — DigestAuth `headerField`
3. `pkg/middlewares/auth/forward.go:304-310` — ForwardAuth `authResponseHeaders` per-name writeback
4. `pkg/middlewares/ingressnginx/snippet/snippet.go:480-486` — Ingress-NGINX snippet `authResponseHeaders` per-name writeback

The ForwardAuth instance (#3) is particularly notable: the attacker does NOT need credentials. The `authResponseHeaders` mechanism is intended to copy identity headers from the trusted auth server only; the underscore-variant bypass lets an unauthenticated attacker pre-inject the same identity header before any auth happens.

The fast proxy at `pkg/proxy/fast/proxy.go:139` explicitly calls `DisableNormalizing()` on the outgoing fasthttp request, guaranteeing that the underscore-variant header reaches the backend wire verbatim. The standard `httputil.ReverseProxy` path at `pkg/proxy/httputil/proxy.go:55` likewise copies `req.Header` keys as-is during the wire write.

## Affected versions

- `traefik` v3.6.x ≤ 3.6.14, v3.7.x ≤ 3.7.0-rc.2, v2.11.x ≤ 2.11.43, and all earlier versions sharing the same auth middleware architecture.

The defect is present at HEAD post-CVE-2026-33433 fix (the fix added the `Del` line but the literal-key write defect-class survives for underscore variants).

## Root cause

In `pkg/middlewares/auth/basic_auth.go` at HEAD `eec68dc`:

```go
if b.headerField != "" {
    // TODO Deprecated we should add the header with canonical key.
    req.Header.Del(b.headerField)
    req.Header[b.headerField] = []string{user}
}
```

The TODO comment shows the maintainer is aware of the literal-key write problem in general (canonical-key write would solve the case-canonicalization issue more cleanly than the current `Del` + literal-write pair). The comment does not acknowledge the underscore-variant survival corollary.

`pkg/middlewares/auth/digest_auth.go:99-103` and the two ForwardAuth paths follow the same `Del` + literal-write pattern. Each is independently exploitable; the underlying primitive defect is shared.

The maintainer's gold-standard primitive for handling this exact threat class is `pkg/middlewares/forwardedheaders/forwarded_header.go:53-66`:

```go
func isManagedXHeader(key string) bool {
    if len(key) == 0 || key[0] != 'X' { return false }
    if _, ok := XHeadersSet[key]; ok { return true }
    if strings.IndexByte(key, '_') < 0 { return false }
    canonical := http.CanonicalHeaderKey(strings.ReplaceAll(key, "_", "-"))
    _, ok := XHeadersSet[canonical]
    return ok
}
```

This treats `_` ↔ `-` equivalence as a security requirement. It is reachable only via the static `XHeadersSet` membership check, which contains exclusively the X-Forwarded-* family + X-Real-Ip. Operator-configurable identity headers are out of scope of this primitive.

## Proof of concept

Verified on `traefik:v3.6.14` (the patched version, post-CVE-2026-33433 and post-CVE-2026-39858) using Docker compose. Full reproducer at https://github.com/<attacker-repo>/traefik-ht1a-poc; commands below are verbatim.

### Setup

```yaml
# docker-compose.yml
services:
  traefik:
    image: traefik:v3.6.14
    command:
      - --providers.file.filename=/etc/traefik/dynamic.yml
      - --entrypoints.web.address=:80
    ports:
      - "8080:80"
    volumes:
      - ./traefik/dynamic.yml:/etc/traefik/dynamic.yml:ro
  echo:
    image: mendhak/http-https-echo:36
    environment:
      - HTTP_PORT=8888
```

```yaml
# traefik/dynamic.yml — canonical headerField, recommended operator config
http:
  routers:
    protected:
      rule: "PathPrefix(`/`)"
      service: echo
      middlewares: [basic-auth]
  services:
    echo:
      loadBalancer:
        servers: [{url: "http://echo:8888"}]
  middlewares:
    basic-auth:
      basicAuth:
        users:
          - 'alice:$2b$05$FhDfYidZdDPuQjovYqcTAe22wHpQ/cILC7Tr2yAD6vLlvZh/Q45PC'   # alice:secret123
        headerField: "X-Auth-User"
```

`docker compose up -d`.

### Test 1 (control — CVE-2026-33433 fix works for canonical case)

```bash
$ curl -s -u alice:secret123 -H "X-Auth-User: superadmin" http://localhost:8080/
{
  ...
  "x-auth-user": "alice",
  ...
}
```

The attacker's canonical `X-Auth-User: superadmin` was correctly stripped by Traefik's `Del`; the backend receives only Traefik's authenticated-user writeback `alice`.

### Test 2 (HT-1A bypass — underscore variant survives)

```bash
$ curl -s -u alice:secret123 -H "X_Auth_User: superadmin" http://localhost:8080/
{
  ...
  "x-auth-user": "alice",
  "x_auth_user": "superadmin",
  ...
}
```

The underscore-variant `x_auth_user: superadmin` reached the backend intact, despite the `Del("X-Auth-User")` having executed. The backend sees both forms.

### Test 3 (double-send — same result)

```bash
$ curl -s -u alice:secret123 \
    -H "X-Auth-User: superadmin" \
    -H "X_Auth_User: superadmin" \
    http://localhost:8080/
{
  ...
  "x-auth-user": "alice",       # Traefik's writeback
  "x_auth_user": "superadmin",  # attacker's underscore — survived Del
  ...
}
```

The canonical attacker header is stripped (Test 1 behavior). The underscore variant is forwarded.

### Backend impact

The PoC's echo backend (`mendhak/http-https-echo`, Node.js) preserves both forms with the lowercase normalization Node.js applies. Application code reading `req.headers["x-auth-user"]` sees `alice`. Application code reading `req.headers["x_auth_user"]` sees `superadmin`.

For backends that normalize `_` ↔ `-` equivalently — meaning the attacker's value wins:

- **CGI / WSGI / PHP `$_SERVER`** (RFC 3875 §4.1.18 — header name uppercased with `-` replaced by `_`): both `X-Auth-User` and `X_Auth_User` map to `HTTP_X_AUTH_USER`. The last-set wins per the WSGI server's iteration order; many servers (gunicorn, uwsgi without `--disable-logging`, waitress) preserve both. Note: Apache + mod_php with default `HttpProtocolOptions Strict` filters underscore-headers from `$_SERVER` (this PoC's PHP backend test demonstrated the filter); Apache + mod_python, Apache + mod_wsgi without the strict mode, nginx + uwsgi, nginx + gunicorn, nginx + FastCGI, and standalone WSGI servers do NOT filter.
- **nginx with `underscores_in_headers on`** (https://nginx.org/en/docs/http/ngx_http_core_module.html#underscores_in_headers): preserves underscore-variant headers and forwards them to upstream as separate values. Upstream application logic that does case-insensitive + underscore-insensitive matching (common pattern in security-sensitive code) merges them.
- **Tomcat / Java EE servlet containers**: `HttpServletRequest.getHeader(name)` is case-insensitive; underscore handling is container-specific. Many normalize.
- **Application middleware** (WAFs, log aggregators, security gateways, identity-aware proxies) that normalize header names before applying security policy: both forms collapse to the same authorization decision input.

## Severity

I propose **HIGH CVSS 7.5** for the BasicAuth / DigestAuth case and **CRITICAL CVSS 9.1** for the ForwardAuth `authResponseHeaders` case (the latter requires no credentials).

**CVSS 3.1 vector (BasicAuth / DigestAuth)**: `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N=7.5` — one step above CVE-2026-33433 (which the maintainer scored MEDIUM 5.1 because it required misconfigured non-canonical `headerField`). HT-1A works against the canonical / recommended `headerField` configuration, broader operational scope.

**CVSS 3.1 vector (ForwardAuth `authResponseHeaders`)**: `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N=9.1` — parallel to CVE-2026-39858 (HIGH 7.5) but achieves spoofing without credentials because the `authResponseHeaders` mechanism trusts headers exclusively from the auth server and the underscore variant defeats that trust boundary.

CWEs:
- CWE-290 (Authentication Bypass by Spoofing)
- CWE-178 (Improper Handling of Case Sensitivity) — analogous to CVE-2026-29054
- CWE-345 (Insufficient Verification of Data Authenticity) — same as CVE-2026-35051

## Suggested fix

Two equivalent approaches:

**1. Extend `Header.Del` to handle underscore variants** at the four call sites. Replace:

```go
req.Header.Del(b.headerField)
req.Header[b.headerField] = []string{user}
```

with:

```go
canonical := http.CanonicalHeaderKey(b.headerField)
// Strip canonical AND underscore-variant of the canonical key.
for key := range req.Header {
    if key == canonical || strings.EqualFold(strings.ReplaceAll(key, "_", "-"), canonical) {
        delete(req.Header, key)
    }
}
req.Header.Set(canonical, user)  // canonical-key write
```

This pairs the headerField primitive with the same `_` ↔ `-` equivalence that `isManagedXHeader` enforces for X-Forwarded-*.

**2. Generalize the existing `isManagedXHeader` primitive** into a `stripHeaderAndVariants(headers http.Header, name string)` helper in the `forwardedheaders` package and call it from `basic_auth.go`, `digest_auth.go`, `forward.go`, and `snippet.go`. Reusing the existing gold-standard primitive is the cleanest fix and minimizes future drift.

Either approach should also resolve the `// TODO Deprecated we should add the header with canonical key.` debt at `basic_auth.go:102` and `digest_auth.go:100` by writing to the canonical key (`Header.Set(canonical, user)`) instead of the literal `b.headerField`.

## Why this is a Pattern-8 sibling, not a new CVE class

The combination of:

1. CVE-2026-33433's fix scope (case-canonicalization for `headerField`)
2. CVE-2026-39858's fix scope (underscore-variant for `XHeadersSet`)
3. The defective primitive remaining at HEAD (the `Del` + literal-write pair at four call sites)

establishes that the maintainer accepts the threat model and has architectural primitives to fix it — but did not cross the two cohorts. The "primitive depth-audit" of the CVE-2026-33433 fix (reading the actual `Header.Del` implementation against the documented threat model and Go's canonicalization semantics) reveals the gap.

I confirmed there is no public PoC mentioning underscore-variant siblings of CVE-2026-33433 (WebSearched 2026-05-23). The fix-flurry from the April 2026 security release batch addressed the X-Forwarded family but not the headerField family.

## Credit

Matteo Panzeri (GitHub `matte1782`). CVE credit requested.

## AI-assistance disclosure

Static analysis, hypothesis writing, and hostile-review confirmation were assisted by Anthropic Claude (Opus 4.7). Live PoC reproduction, code-citation verification, and submission decision were made by the human author.


</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-x677-9fxg-v5c5
- https://nvd.nist.gov/vuln/detail/CVE-2026-54763
- https://github.com/traefik/traefik/pull/13262
- https://github.com/traefik/traefik/commit/108a5264473a2cbc8f12d6d691a3c6553cdf2c1b
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.51
- https://github.com/traefik/traefik/releases/tag/v3.6.22
- https://github.com/traefik/traefik/releases/tag/v3.7.6
