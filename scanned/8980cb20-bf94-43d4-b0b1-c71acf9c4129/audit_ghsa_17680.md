# [M] kro Confused Deputy vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7633-x85h-5mqh
CVE: CVE-2025-48710
CWE: CWE-441
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-7633-x85h-5mqh
Type: github-advisory

## Affected
- Go: `github.com/kro-run/kro` — affected >=0.1.0 <0.2.1

## Details
kro (Kube Resource Orchestrator) 0.1.0 before 0.2.1 allows users (with permission to create or modify ResourceGraphDefinition resources) to supply arbitrary container images. This can lead to a confused-deputy scenario where kro's controllers deploy and run attacker-controlled images, resulting in unauthenticated remote code execution on cluster nodes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48710
- https://github.com/kro-run/kro
- https://github.com/kro-run/kro/compare/v0.2.1...v0.2.2
- https://orca.security/resources/blog/kubernetes-crd-abstraction-risks-kro
