# [M] BIT-envoy-2020-8660

## Summary
Severity: Medium
Advisory: BIT-envoy-2020-8660
Aliases: CVE-2020-8660, GHSA-c4g8-7grc-5wvx
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2020-8660
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.13.0 <1.13.1

## Details
CNCF Envoy through 1.13.0 TLS inspector bypass. TLS inspector could have been bypassed (not recognized as a TLS client) by a client using only TLS 1.3. Because TLS extensions (SNI, ALPN) were not inspected, those connections might have been matched to a wrong filter chain, possibly bypassing some security restrictions in the process.

## References
- https://access.redhat.com/errata/RHSA-2020:0734
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-c4g8-7grc-5wvx
- https://www.envoyproxy.io/docs/envoy/v1.13.1/intro/version_history
- https://nvd.nist.gov/vuln/detail/CVE-2020-8660
