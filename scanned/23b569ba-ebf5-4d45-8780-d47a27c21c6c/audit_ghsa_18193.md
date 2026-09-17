# [H] Chaos Mesh's Chaos Controller Manager is Missing Authentication for Critical Function

## Summary
Severity: High
Advisory: GHSA-2gg8-85m5-8r2p
CVE: CVE-2025-59358
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-2gg8-85m5-8r2p
Type: github-advisory

## Affected
- Go: `github.com/chaos-mesh/chaos-mesh` — affected >=0 <2.7.3

## Details
The Chaos Controller Manager in Chaos Mesh exposes a GraphQL debugging server without authentication to the entire Kubernetes cluster, which provides an API to kill arbitrary processes in any Kubernetes pod, leading to cluster-wide denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59358
- https://github.com/chaos-mesh/chaos-mesh/pull/4702
- https://github.com/chaos-mesh/chaos-mesh/commit/67281c36f8068bf103149318cd0a466417213a28
- https://github.com/chaos-mesh/chaos-mesh
- https://jfrog.com/blog/chaotic-deputy-critical-vulnerabilities-in-chaos-mesh-lead-to-kubernetes-cluster-takeover
