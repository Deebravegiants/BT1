# [H] BIT-envoy-2020-8663

## Summary
Severity: High
Advisory: BIT-envoy-2020-8663
Aliases: CVE-2020-8663, GHSA-v8q7-fq78-4997
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2020-8663
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.14.0 <1.14.3

## Details
Envoy version 1.14.2, 1.13.2, 1.12.4 or earlier may exhaust file descriptors and/or memory when accepting too many connections.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-v8q7-fq78-4997
- https://www.envoyproxy.io/docs/envoy/v1.13.1/intro/version_history
- https://nvd.nist.gov/vuln/detail/CVE-2020-8663
