# [M] Docker Sandboxes ICMP egress restriction bypass after daemon restart

## Summary
Severity: Medium
Advisory: CVE-2026-12539
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-12539
Type: osv

## Details
Docker Sandboxes (sbx) blocks ICMP egress with an authorizer applied only at network-creation time, and does not re-apply it to networks rebuilt from disk when the Docker daemon restarts, so a restart-surviving sandbox forwards ICMP to arbitrary hosts. A workload inside a sandbox, which the threat model treats as untrusted, can therefore defeat the documented ICMP egress block to perform network reconnaissance and exfiltrate data over an ICMP covert channel, regardless of the configured allowlist.

## References
- https://docs.docker.com/ai/sandboxes/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12539.json
- https://github.com/docker/sbx-releases/releases/tag/v0.33.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-12539
