# [H] Arc: Unauthenticated access to Go debug pprof endpoints leaks runtime state and enables CPU-burn DoS

## Summary
Severity: High
Advisory: GHSA-j93g-rp6m-j32m
CVE: CVE-2026-48050
CWE: CWE-200, CWE-306, CWE-400
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-j93g-rp6m-j32m
Type: github-advisory

## Affected
- Go: `github.com/basekick-labs/arc` — affected >=0 <0.0.0-20260520170331-32a4091fb949

## Details
### Summary

Arc registers Go's `net/http/pprof` handlers at `/debug/pprof/*` via `app.Use(pprof.New())` in `internal/api/server.go`, and `/debug/pprof` is added to `PublicPrefixes` in `cmd/arc/main.go`. The auth middleware short-circuits before the token check on prefix match, so the endpoints are reachable without any authentication.

### Impact

Any network-reachable caller (no token required) can:

- Fetch `/debug/pprof/heap` — leaks in-memory state: live SQL strings, decoded msgpack records, decompressed request bodies, cached `*TokenInfo` (the auth cache keys on SHA-256 of the plaintext token at `auth.go:543`).
- Fetch `/debug/pprof/goroutine?debug=2` — leaks call stacks, identifying internal code paths.
- Fetch `/debug/pprof/profile?seconds=N` — pins a CPU core for arbitrary duration. Trivial DoS amplification (one short HTTP request → minutes of server CPU).
- Fetch `/debug/pprof/trace` — long-duration execution trace, similar DoS profile.

No authentication, no rate limiting, no resource bound on the `seconds` parameter.

### Patches

https://github.com/Basekick-Labs/arc/releases/tag/v26.06.1

Planned mitigation:

1. Gate pprof registration behind an env var (`ARC_DEBUG_PPROF=1`) that defaults to off.
2. When enabled, bind pprof to a separate localhost-only listener (`127.0.0.1:6060` via dedicated `net/http` server) so it's never reachable from the public API port.
3. Remove `/debug/pprof` from `PublicPrefixes`.
4. Fix the `HasPrefix` bug where `"/debug/pprofX"` matches `"/debug/pprof"`.

### Workarounds

- Block `/debug/pprof*` at a reverse proxy / load balancer in front of Arc.
- Restrict Arc's API port to known-trusted networks via firewall rules.
- Patch the running build: comment out `app.Use(pprof.New())` in `internal/api/server.go` and rebuild.

### Credits

Reported by Alex Manson ([@NeuroWinter](https://github.com/NeuroWinter), https://neurowinter.com/) on 2026-05-19.

## References
- https://github.com/Basekick-Labs/arc/security/advisories/GHSA-j93g-rp6m-j32m
- https://github.com/Basekick-Labs/arc/commit/32a4091fb949f9cf060cdd804a07f6450dc426a8
- https://github.com/Basekick-Labs/arc
- https://github.com/Basekick-Labs/arc/releases/tag/v26.06.1
