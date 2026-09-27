# [M] Docker Sandboxes network egress allowlist bypass via unfiltered DNS resolution

## Summary
Severity: Medium
Advisory: CVE-2026-12039
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-12039
Type: osv

## Details
Docker Sandboxes (sbx) enforces an HTTP/S-only egress allowlist but does not apply it to DNS resolution: the per-network embedded DNS server forwards any queried name to the host resolver whenever the network is internet-connected, without consulting the policy. A workload inside a sandbox, which the threat model treats as untrusted, can therefore encode data into DNS labels for an attacker-controlled domain and exfiltrate it through a DNS covert channel, bypassing the configured allowlist.

## References
- https://docs.docker.com/ai/sandboxes/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12039.json
- https://github.com/docker/sbx-releases/releases/tag/v0.33.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-12039
