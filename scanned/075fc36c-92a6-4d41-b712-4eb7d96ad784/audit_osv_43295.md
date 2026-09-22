# [M] coturn: mobility disconnects bypass allocation quotas and exhaust relay capacity

## Summary
Severity: Medium
Advisory: CVE-2026-73216
Aliases: GHSA-f6hc-79w3-p8pq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73216
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. Prior to 4.17.0, shutdown_client_connection() in src/server/ns_turn_server.c prematurely calls dec_quota() and releases bandwidth accounting during the first-stage close of a mobility-enabled allocation while preserving the allocation, relay socket, session, and mobility ticket, allowing an authenticated client to bypass --user-quota and --total-quota and exhaust relay ports. This issue is fixed in version 4.17.0.

## References
- https://github.com/coturn/coturn/releases/tag/4.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73216.json
- https://github.com/coturn/coturn/security/advisories/GHSA-f6hc-79w3-p8pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-73216
- https://github.com/coturn/coturn/commit/3c5b2615fd405c4e7c5bf3fbeef895c94a90671b
