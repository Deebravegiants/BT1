# [M] Sigstore Timestamp Authority has OOM due to unbounded metric label cardinality

## Summary
Severity: Medium
Advisory: GHSA-9c54-x2g4-v92j
CVE: CVE-2026-49835
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-9c54-x2g4-v92j
Type: github-advisory

## Affected
- Go: `github.com/sigstore/timestamp-authority/v2` — affected >=0 <2.1.0
- Go: `github.com/sigstore/timestamp-authority` — affected >=0

## Details
### Impact

An unauthenticated remote attacker can trigger unbounded memory growth on the timestamp authority server.

This vulnerability exists because the global `wrapMetrics` middleware records the raw HTTP request path (`r.URL.Path`) and raw HTTP request method (`r.Method`) as Prometheus labels for latency and request count metric vectors. Since this middleware runs before standard routing occurs, it executes for all incoming requests, including those for unmatched paths (yielding 404 responses) or arbitrary request methods. The Prometheus library registers a new, permanent time-series entry for every distinct label combination. An attacker can continuously issue requests containing random paths (e.g., `/api/v1/timestamp/<uuid>`) or random HTTP methods to exhaust system memory.

### Patches

This issue has been patched by limiting the metric label values to a strict allowlist of expected paths (`/ping`, `/api/v1/timestamp`, `/api/v1/timestamp/certchain`) and expected HTTP methods (`GET`, `POST`, `HEAD`, `OPTIONS`). Unrecognized paths or methods are normalized to a static string (`"unrecognized"`).

Users should update to version `v2.0.7` or later.

### Workarounds

1. Block or drop incoming requests with invalid HTTP methods or unknown request paths at a reverse proxy or load balancer before they reach the timestamp authority server.
2. Configure rate-limiting on the public interface to prevent remote attackers from issuing millions of unique requests in a short duration.

## References
- https://github.com/sigstore/timestamp-authority/security/advisories/GHSA-9c54-x2g4-v92j
- https://github.com/sigstore/timestamp-authority
