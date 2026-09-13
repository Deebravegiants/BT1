# [M] External Secrets Operator has Namespace Isolation Bypass in CAProvider ConfigMap Resolution for SecretStore

## Summary
Severity: Medium
Advisory: GHSA-wv26-88m5-6h59
CVE: CVE-2026-42875
CWE: CWE-285, CWE-668
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-wv26-88m5-6h59
Type: github-advisory

## Affected
- Go: `github.com/external-secrets/external-secrets` — affected >=0 <2.4.0

## Details
### Impact

Namespaced SecretStore resources that used CAProvider with type `ConfigMap` could resolve CA material from another namespace when `caProvider.namespace` was set. 
This bypassed the namespace boundary enforced for SecretStore-backed references in providers that rely on the shared runtime CA resolver. 

The accessible data is used as CA validation material, hence it is not directly exposed.

Impact:
- Direct data exfiltration risk: low
- Existence disclosure: an attacker can infer whether a target ConfigMap/key exists in another namespace.
- Trust-boundary violation: a tenant can make its SecretStore consume CA material owned by another namespace.

## References
- https://github.com/external-secrets/external-secrets/security/advisories/GHSA-wv26-88m5-6h59
- https://nvd.nist.gov/vuln/detail/CVE-2026-42875
- https://github.com/external-secrets/external-secrets
