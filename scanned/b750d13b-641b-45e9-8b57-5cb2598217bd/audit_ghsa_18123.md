# [C] Chaos Controller Manager is vulnerable to OS command injection

## Summary
Severity: Critical
Advisory: GHSA-xv9f-728h-9jgv
CVE: CVE-2025-59360
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-xv9f-728h-9jgv
Type: github-advisory

## Affected
- Go: `github.com/chaos-mesh/chaos-mesh` — affected >=0 <2.7.3

## Details
The killProcesses mutation in Chaos Controller Manager is vulnerable to OS command injection. In conjunction with CVE-2025-59358, this allows unauthenticated in-cluster attackers to perform remote code execution across the cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59360
- https://github.com/chaos-mesh/chaos-mesh/pull/4702
- https://github.com/chaos-mesh/chaos-mesh/commit/67281c36f8068bf103149318cd0a466417213a28
- https://github.com/chaos-mesh/chaos-mesh
- https://jfrog.com/blog/chaotic-deputy-critical-vulnerabilities-in-chaos-mesh-lead-to-kubernetes-cluster-takeover
