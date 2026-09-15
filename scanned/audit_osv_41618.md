# [M] ws < 8.21.1 Default maxFragments Allows Memory Exhaustion DoS

## Summary
Severity: Medium
Advisory: CVE-2026-62389
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-62389
Type: osv

## Details
ws before 8.21.1 contains a memory exhaustion vulnerability in lib/receiver.js where the fragment guard only triggers when fragment count reaches maxFragments, allowing attackers to exhaust memory by sending incomplete fragmented WebSocket messages. Attackers can send a text frame with FIN=0 followed by continuation frames without completing the sequence, causing each fragment to be stored as a separate Buffer object with significant overhead, enabling denial of service through heap exhaustion.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62389.json
- https://github.com/websockets/ws/releases/tag/8.21.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-62389
- https://www.vulncheck.com/advisories/ws-default-maxfragments-allows-memory-exhaustion-dos
- https://github.com/websockets/ws/commit/f197ac65140920bdcecdab74bfc69c2d7858e55d
- https://github.com/websockets/ws
- https://github.com/websockets/ws/issues/2331
