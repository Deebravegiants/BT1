# [M] nebula-mesh: Unauthenticated OIDC login endpoint allocates unbounded in-memory state entries without rate limiting

## Summary
Severity: Medium
Advisory: GHSA-m3cx-mwpg-32jg
CVE: CVE-2026-55512
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-m3cx-mwpg-32jg
Type: github-advisory

## Affected
- Go: `github.com/forgekeep/nebula-mesh` — affected >=0.2.0 <0.5.0

## Details
### Summary
When OIDC is enabled, `GET /ui/oidc/login` is reachable without authentication and is registered outside the Web UI rate-limited auth routes. Every request creates a fresh random OIDC state value and stores it in an in-memory map for `10m`. Expired states are swept lazily, but there is no rate limit or maximum live-state cap on the allocation path. An unauthenticated remote client can therefore grow `OIDC.states` for the full state TTL, bounded by request throughput rather than by configured auth rate limits.

### Details
The OIDC login route is registered directly by `WithOIDC`:

- `internal/web/web.go:153` registers `w.router.Get("/ui/oidc/login", o.HandleLogin)`.
- `internal/web/web.go:154` rate-limits only `GET /ui/oidc/callback` with `w.rateLimitMiddleware("auth")`.

The normal `/ui/*` route group applies rate limiting to login/register form submissions, but this direct registration happens outside that group:

- `internal/web/web.go:287` through `internal/web/web.go:292` show the rate-limited local login, TOTP, and register POST routes.

The OIDC login handler allocates persistent server-side state before redirecting to the configured identity provider:

- `internal/web/oidc.go:105` defines `HandleLogin`.
- `internal/web/oidc.go:106` creates a random state token.
- `internal/web/oidc.go:112` calls `o.rememberState(state)`.
- `internal/web/oidc.go:122` redirects to `o.oauth.AuthCodeURL(state)`.

The state storage has a TTL but no maximum size:

- `internal/web/oidc.go:24` through `internal/web/oidc.go:26` define `oidcStateTTL = 10 * time.Minute`.
- `internal/web/oidc.go:353` through `internal/web/oidc.go:358` sweep expired states and then add the new state to `o.states`.
- `internal/web/oidc.go:360` through `internal/web/oidc.go:373` delete only expired states.

Because the route is unauthenticated and not rate-limited, a remote client can repeatedly request `/ui/oidc/login` and force live state entries to accumulate for ten minutes. OIDC must be enabled for exposure. No IdP callback, valid credentials, or user interaction is required to trigger the allocation.

Affected version evidence: OIDC login support was introduced by commit `3f46685` (`feat(auth): add OIDC operator login (Keycloak/Authentik/Okta/...) (#24)`), and `git tag --contains 3f46685 --sort=version:refname` returns `v0.2.0` and every later release through `v0.3.8`. Pattern checks across all release tags showed the OIDC login route and state allocation are present in `v0.2.0` and in every `v0.3.x` release from `v0.3.0` to `v0.3.8`, and absent from `v0.1.x`. The current checkout at commit `d92dd9a60de291e2bc1caf73b4e9a99567b31ec0` (`git describe`: `v0.3.8-1-gd92dd9a`) remains affected.

### PoC
Safe local PoC run from a clean checkout at commit `d92dd9a60de291e2bc1caf73b4e9a99567b31ec0` on 2026-06-12. The PoC is a temporary Go test that uses `httptest` and an in-memory OIDC object; it does not start a real server, does not contact an IdP, and uses 1000 requests only to demonstrate linear state growth.

1. Create a temporary test file `internal/web/security_audit_poc_test.go` in package `web`.
2. Create a test Web UI with `newTestWeb(t)`.
3. Install a deliberately tiny auth rate limiter: group `auth` with rate `0.001` and burst `2`.
4. Attach an `OIDC` instance with an empty `states` map and an `oauth2.Config` whose authorization endpoint is `https://idp.example.test/auth`.
5. Send 1000 unauthenticated `GET /ui/oidc/login` requests from the same `RemoteAddr` through `w.ServeHTTP`.
6. Assert no request returns `429 Too Many Requests`, then inspect `o.stateCount()`.

Command run:

```bash
go test ./internal/web -run 'TestSecurityAuditPOC' -count=1 -v
```

Observed vulnerable output from this environment:

```text
=== RUN   TestSecurityAuditPOC_OIDCLoginAllocatesUnrateLimitedState
POC_OIDC_STATE_GROWTH attempts=1000 live_states=1000 ttl=10m0s rate_limit_group=auth_burst_2
--- PASS: TestSecurityAuditPOC_OIDCLoginAllocatesUnrateLimitedState (0.10s)
```

The meaningful control is that local login/register/TOTP POST routes and the OIDC callback are rate-limited: `internal/web/web.go:287` through `internal/web/web.go:292` and `internal/web/web.go:154`. The PoC specifically shows the OIDC login allocation route does not share that protection. After recording the output, the temporary test file was removed and `git status --short` returned clean. The PoC was re-run after drafting this report and produced the output shown above.

### Impact
In deployments with OIDC enabled, an unauthenticated remote client can cause application-layer memory growth by repeatedly requesting `/ui/oidc/login`. Each request stores a new state entry for ten minutes, and the growth is not bounded by the configured auth rate limiter or by a maximum map size. The demonstrated impact is availability degradation risk through retained in-memory state growth. The PoC used 1000 local requests to avoid disruptive load while proving the source-to-sink behavior (`1000` requests resulted in `1000` live states).

Suggested remediation: apply the existing `auth` rate limiter to `GET /ui/oidc/login`, add a maximum number of live OIDC states per client and/or globally, and fail closed when the cap is reached. Add a regression test that attaches a low-burst auth limiter, sends repeated `GET /ui/oidc/login` requests from the same client, and expects `429` or bounded live-state count after the configured burst.

## References
- https://github.com/forgekeep/nebula-mesh/security/advisories/GHSA-m3cx-mwpg-32jg
- https://github.com/forgekeep/nebula-mesh/commit/bc387086cc0e4b9c1654468b7391af19cacfe367
- https://github.com/forgekeep/nebula-mesh
- https://github.com/forgekeep/nebula-mesh/releases/tag/v0.5.0
