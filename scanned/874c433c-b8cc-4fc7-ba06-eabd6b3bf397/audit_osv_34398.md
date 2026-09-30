# [C] OS command injection in Chaos Mesh via the cleanIptables mutation

## Summary
Severity: Critical
Advisory: CVE-2025-59361
Aliases: GHSA-2gcv-3qpf-c5qr, GO-2025-3949
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-59361
Type: osv

## Details
The cleanIptables mutation in Chaos Controller Manager is vulnerable to OS command injection. In conjunction with CVE-2025-59358, this allows unauthenticated in-cluster attackers to perform remote code execution across the cluster.

## References
- https://go.dev
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59361.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59361
- https://github.com/chaos-mesh/chaos-mesh/pull/4702
- https://jfrog.com/blog/chaotic-deputy-critical-vulnerabilities-in-chaos-mesh-lead-to-kubernetes-cluster-takeover
