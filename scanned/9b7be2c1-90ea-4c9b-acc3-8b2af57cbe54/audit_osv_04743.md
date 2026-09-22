# [H] BIT-envoy-2020-12605

## Summary
Severity: High
Advisory: BIT-envoy-2020-12605
Aliases: CVE-2020-12605, GHSA-fjxc-jj43-f777
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2020-12605
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.14.2 <1.14.3

## Details
Envoy version 1.14.2, 1.13.2, 1.12.4 or earlier may consume excessive amounts of memory when processing HTTP/1.1 headers with long field names or requests with long URLs.

## References
- https://github.com/envoyproxy/envoy-setec/issues/137
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-fjxc-jj43-f777
- https://nvd.nist.gov/vuln/detail/CVE-2020-12605
