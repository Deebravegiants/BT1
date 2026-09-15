# [H] Envoy vulnerable to incorrect handling of HTTP requests and responses with mixed case schemes

## Summary
Severity: High
Advisory: BIT-envoy-2023-35944
Aliases: CVE-2023-35944, GHSA-pvgm-7jpg-pw5g
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2023-35944
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.26.0 <1.26.4

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Envoy allows mixed-case schemes in HTTP/2, however, some internal scheme checks are case-sensitive. Prior to versions 1.27.0, 1.26.4, 1.25.9, 1.24.10, and 1.23.12, this can lead to the rejection of requests with mixed-case schemes such as `htTp` or `htTps`, or the bypassing of some requests such as `https` in unencrypted connections. With a fix in versions 1.27.0, 1.26.4, 1.25.9, 1.24.10, and 1.23.12, Envoy will now lowercase scheme values by default, and change the internal scheme checks that were case-sensitive to be case-insensitive. There are no known workarounds for this issue.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-pvgm-7jpg-pw5g
- https://nvd.nist.gov/vuln/detail/CVE-2023-35944
