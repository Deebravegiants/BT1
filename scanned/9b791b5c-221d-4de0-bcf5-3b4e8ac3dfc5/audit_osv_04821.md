# [M] Envoy HTTP: OAuth2 filter late async token completion after stream teardown (UAF / crash risk)

## Summary
Severity: Medium
Advisory: BIT-envoy-2026-48090
Aliases: CVE-2026-48090, GHSA-3cj2-c63f-q26f
Ecosystem: Bitnami
Published: 2026-06-30
Source: https://osv.dev/vulnerability/BIT-envoy-2026-48090
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.38.0 <1.38.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. From 1.37.0 until 1.37.5 and 1.38.3, the HTTP OAuth2 filter (envoy.filters.http.oauth2) can leave an in-flight async token exchange attached to a downstream stream that has already been torn down. A late AsyncClient completion can still invoke OAuth2Filter methods that use StreamDecoderFilterCallbacks after that object’s lifetime has ended, causing undefined behavior, worker crashes (availability loss), and use-after-free / invalid-vptr failures under AddressSanitizer. This is a memory-safety / lifetime issue in the data plane, not a trivial config bug. Remote code execution is not claimed here; the primary demonstrated impact is DoS via crash and UB; any further impact would be deployment- and allocator-dependent.  This vulnerability is fixed in 1.37.5 and 1.38.3.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-3cj2-c63f-q26f
- https://nvd.nist.gov/vuln/detail/CVE-2026-48090
