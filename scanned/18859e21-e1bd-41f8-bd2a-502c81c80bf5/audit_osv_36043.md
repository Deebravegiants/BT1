# [M] CVE-2026-19204

## Summary
Severity: Medium
Advisory: CVE-2026-19204
Aliases: GHSA-85fq-fc5f-7j7g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-19204
Type: osv

## Details
A client may send a WebSocket frame with an unknown opcode and a very large declared payload length, causing Jetty to attempt a large memory allocation and potentially exhaust the JVM heap.




This occurs when auto-fragmentation is enabled, as unknown opcodes bypass the normal maximum frame size handling and payload allocation occurs before the opcode is validated.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19204.json
- https://github.com/jetty/jetty.project/security/advisories/GHSA-85fq-fc5f-7j7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-19204
