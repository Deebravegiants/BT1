# [H] BIT-envoy-2020-25017

## Summary
Severity: High
Advisory: BIT-envoy-2020-25017
Aliases: CVE-2020-25017, GHSA-2v25-cjjq-5f4w
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2020-25017
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.15.0 <1.15.1

## Details
Envoy through 1.15.0 only considers the first value when multiple header values are present for some HTTP headers. Envoy’s setCopy() header map API does not replace all existing occurences of a non-inline header.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-2v25-cjjq-5f4w
- https://groups.google.com/forum/#%21forum/envoy-security-announce
- https://nvd.nist.gov/vuln/detail/CVE-2020-25017
