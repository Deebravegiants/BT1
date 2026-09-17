# [M] Unbounded Memory Allocation in VQLResponse Result-Set Writer

## Summary
Severity: Medium
Advisory: CVE-2026-6948
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-03
Source: https://osv.dev/vulnerability/CVE-2026-6948
Type: osv

## Details
Velociraptor versions prior to 0.76.4 contain a resource exhaustion vulnerability in the server's agent control channel.



This allows a compromised or rogue Velociraptor client to crash the server via out-of-memory (OOM) by sending crafted messages through the normal client communication channel.

## References
- https://docs.velociraptor.app/announcements/advisories/cve-2026-6948/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6948.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6948
- https://github.com/Velocidex/velociraptor
