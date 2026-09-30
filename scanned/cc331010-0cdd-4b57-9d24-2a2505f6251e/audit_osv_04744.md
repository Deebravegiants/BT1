# [M] TLS Validation Vulnerability in Envoy

## Summary
Severity: Medium
Advisory: BIT-envoy-2020-15104
Aliases: CVE-2020-15104, GHSA-w5f5-6qhq-hhrg
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2020-15104
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.14.0 <1.14.4

## Details
In Envoy before versions 1.12.6, 1.13.4, 1.14.4, and 1.15.0 when validating TLS certificates, Envoy would incorrectly allow a wildcard DNS Subject Alternative Name apply to multiple subdomains. For example, with a SAN of *.example.com, Envoy would incorrectly allow nested.subdomain.example.com, when it should only allow subdomain.example.com. This defect applies to both validating a client TLS certificate in mTLS, and validating a server TLS certificate for upstream connections. This vulnerability is only applicable to situations where an untrusted entity can obtain a signed wildcard TLS certificate for a domain of which you only intend to trust a subdomain of. For example, if you intend to trust api.mysubdomain.example.com, and an untrusted actor can obtain a signed TLS certificate for *.example.com or *.com. Configurations are vulnerable if they use verify_subject_alt_name in any Envoy version, or if they use match_subject_alt_names in version 1.14 or later. This issue has been fixed in Envoy versions 1.12.6, 1.13.4, 1.14.4, 1.15.0.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-w5f5-6qhq-hhrg
- https://nvd.nist.gov/vuln/detail/CVE-2020-15104
