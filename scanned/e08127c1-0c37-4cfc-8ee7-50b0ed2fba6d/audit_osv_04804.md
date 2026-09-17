# [C] BIT-envoy-2024-7207

## Summary
Severity: Critical
Advisory: BIT-envoy-2024-7207
Aliases: CVE-2024-7207
Ecosystem: Bitnami
Published: 2024-09-26
Source: https://osv.dev/vulnerability/BIT-envoy-2024-7207
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.31.0 <1.31.2

## Details
A flaw was found in Envoy. It is possible to modify or manipulate headers from external clients when pass-through routes are used for the ingress gateway. This issue could allow a malicious user to forge what is logged by Envoy as a requested path and cause the Envoy proxy to make requests to internal-only services or arbitrary external systems. This is a regression of the fix for CVE-2023-27487.

## References
- https://access.redhat.com/security/cve/CVE-2024-7207
- https://bugzilla.redhat.com/show_bug.cgi?id=2300352
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-ffhv-fvxq-r6mf
