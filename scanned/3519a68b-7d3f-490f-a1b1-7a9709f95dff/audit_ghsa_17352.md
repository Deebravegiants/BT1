# [M] Envoy crashes when JWT authentication is configured with the remote JWKS fetching

## Summary
Severity: Medium
Advisory: GHSA-mp85-7mrq-r866
CVE: CVE-2025-64527
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-05
Source: https://github.com/advisories/GHSA-mp85-7mrq-r866
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/envoy` — affected >=1.36.0 <1.36.3
- Go: `github.com/envoyproxy/envoy` — affected >=1.35.0 <1.35.7
- Go: `github.com/envoyproxy/envoy` — affected >=1.34.0 <1.34.11
- Go: `github.com/envoyproxy/envoy` — affected >=0 <1.33.13

## Details
### Summary
Envoy crashes when JWT authentication is configured with the remote JWKS fetching, `allow_missing_or_failed` is enabled, multiple JWT tokens are present in the request headers and the JWKS fetch fails.

### Details
This is caused by a re-entry bug in the `JwksFetcherImpl`. When the first token's JWKS fetch fails, `onJwksError()` callback triggers processing of the second token, which calls fetch() again on the same fetcher object.

The original callback's reset() then clears the second fetch's state (`receiver_ and request_`) which causes a crash when the async HTTP response arrives.

### PoC
* `allow_missing_or_failed` or `allow_missing` is enabled
* The client send 2 Authorization headers
* the remote JWKS fetching failed
* There will be crash

### Impact
DoS and Crash

### Mitigation
* Disable the `allow_missing_or_failed` or `allow_missing`

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-mp85-7mrq-r866
- https://nvd.nist.gov/vuln/detail/CVE-2025-64527
- https://github.com/envoyproxy/envoy
