# [H] MARIN3R: Cross-Namespace Vulnerability in the Operator

## Summary
Severity: High
Advisory: GHSA-gf93-xccm-5g6j
CVE: CVE-2025-64171
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-04
Source: https://github.com/advisories/GHSA-gf93-xccm-5g6j
Type: github-advisory

## Affected
- Go: `github.com/3scale-sre/marin3r` — affected >=0 <0.13.4

## Details
## Summary
Cross-namespace Secret access vulnerability in DiscoveryServiceCertificate 
allows users to bypass RBAC and access Secrets in unauthorized namespaces.

## Affected Versions
All versions prior to v0.13.4

## Patched Versions
v0.13.4 and later

## Impact
Users with permission to create DiscoveryServiceCertificate resources in one 
namespace can indirectly read Secrets from other namespaces, completely 
bypassing Kubernetes RBAC security boundaries.

## Workarounds
Restrict DiscoveryServiceCertificate create permissions to cluster administrators 
only until patched version is deployed.

## Credit
Thanks to @debuggerchen for the responsible disclosure.

## References
- https://github.com/3scale-sre/marin3r/security/advisories/GHSA-gf93-xccm-5g6j
- https://nvd.nist.gov/vuln/detail/CVE-2025-64171
- https://github.com/3scale-sre/marin3r/pull/294
- https://github.com/3scale-sre/marin3r/commit/859b14115fde1d67620e645cd1b62e90e30d9981
- https://github.com/3scale-sre/marin3r/commit/c60246a43ae8c0c38dd7267f298d68a121a159fa
- https://github.com/3scale-sre/marin3r
