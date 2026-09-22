# [H] Envoy RELEASE_ASSERT using auto_sni with :authority header > 255 bytes

## Summary
Severity: High
Advisory: BIT-envoy-2024-32475
Aliases: CVE-2024-32475, GHSA-3mh5-6q8v-25wj
Ecosystem: Bitnami
Published: 2024-04-20
Source: https://osv.dev/vulnerability/BIT-envoy-2024-32475
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.30.0 <1.30.1

## Details
Envoy is a cloud-native, open source edge and service proxy. When an upstream TLS cluster is used with `auto_sni` enabled, a request containing a `host`/`:authority` header longer than 255 characters triggers an abnormal termination of Envoy process. Envoy does not gracefully handle an error when setting SNI for outbound TLS connection. The error can occur when Envoy attempts to use the `host`/`:authority` header value longer than 255 characters as SNI for outbound TLS connection. SNI length is limited to 255 characters per the standard. Envoy always expects this operation to succeed and abnormally aborts the process when it fails. This vulnerability is fixed in 1.30.1, 1.29.4, 1.28.3, and 1.27.5.

## References
- https://github.com/envoyproxy/envoy/commit/b47fc6648d7c2dfe0093a601d44cb704b7bad382
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-3mh5-6q8v-25wj
- https://nvd.nist.gov/vuln/detail/CVE-2024-32475
