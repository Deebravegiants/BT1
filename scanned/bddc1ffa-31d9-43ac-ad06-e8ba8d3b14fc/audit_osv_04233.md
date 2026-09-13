# [M] authentik allows a timing attack due to missing constant time comparison for metrics view

## Summary
Severity: Medium
Advisory: BIT-authentik-2024-52307
Aliases: CVE-2024-52307, GHSA-2xrw-5f2x-m56j
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2024-52307
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2024.10.0 <2024.10.3

## Details
authentik is an open-source identity provider. Due to the usage of a non-constant time comparison for the /-/metrics/ endpoint it was possible to brute-force the SECRET_KEY, which is used to authenticate the endpoint. The /-/metrics/ endpoint returns Prometheus metrics and is not intended to be accessed directly, as the Go proxy running in the authentik server container fetches data from this endpoint and serves it on a separate port (9300 by default), which can be scraped by Prometheus without being exposed publicly. authentik 2024.8.5 and 2024.10.3 fix this issue. Since the /-/metrics/ endpoint is not intended to be accessed publicly, requests to the endpoint can be blocked by the reverse proxy/load balancer used in conjunction with authentik.

## References
- http://www.openwall.com/lists/oss-security/2024/11/27/1
- https://github.com/goauthentik/authentik/commit/5ea4580884f99369f0ccfe484c04cb03a66e65b8
- https://github.com/goauthentik/authentik/security/advisories/GHSA-2xrw-5f2x-m56j
- https://nvd.nist.gov/vuln/detail/CVE-2024-52307
