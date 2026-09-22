# [H] Envoy incorrectly accepts HTTP 200 response for entering upgrade mode

## Summary
Severity: High
Advisory: BIT-envoy-2024-23326
Aliases: CVE-2024-23326, GHSA-vcf8-7238-v74c
Ecosystem: Bitnami
Published: 2024-06-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-23326
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.30.0 <1.30.2

## Details
Envoy is a cloud-native, open source edge and service proxy. A theoretical request smuggling vulnerability exists through Envoy if a server can be tricked into adding an upgrade header into a response. Per RFC https://www.rfc-editor.org/rfc/rfc7230#section-6.7 a server sends 101 when switching protocols. Envoy incorrectly accepts a 200 response from a server when requesting a protocol upgrade, but 200 does not indicate protocol switch. This opens up the possibility of request smuggling through Envoy if the server can be tricked into adding the upgrade header to the response.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-vcf8-7238-v74c
- https://nvd.nist.gov/vuln/detail/CVE-2024-23326
