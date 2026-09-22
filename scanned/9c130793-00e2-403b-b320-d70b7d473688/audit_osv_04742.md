# [H] BIT-envoy-2020-12604

## Summary
Severity: High
Advisory: BIT-envoy-2020-12604
Aliases: CVE-2020-12604, GHSA-8hf8-8gvw-ggvx
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2020-12604
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.14.2 <1.14.3

## Details
Envoy version 1.14.2, 1.13.2, 1.12.4 or earlier is susceptible to increased memory usage in the case where an HTTP/2 client requests a large payload but does not send enough window updates to consume the entire stream and does not reset the stream.

## References
- https://github.com/envoyproxy/envoy/commits/master
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-8hf8-8gvw-ggvx
- https://nvd.nist.gov/vuln/detail/CVE-2020-12604
