# [M] Libevent: Null Pointer Dereference in `evws_new_session`

## Summary
Severity: Medium
Advisory: CVE-2026-63380
Aliases: GHSA-3rpf-frgx-xq34
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-63380
Type: osv

## Details
Libevent is an event notification library. Prior to 2.2.2-alpha, libevent can dereference invalid list pointers in ws.c when evws_new_session enters its error path after evhttp_start_ws_ succeeds but bufferevent_enable_locking_ fails. evws_connection_free sees a non-null http_server and unconditionally calls TAILQ_REMOVE even though the session was never inserted into http_server->ws_sessions. A local caller able to induce this allocation or locking failure can crash the process. This issue is fixed in version 2.2.2-alpha.

## References
- https://github.com/libevent/libevent/releases/tag/release-2.2.2-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63380.json
- https://github.com/libevent/libevent/security/advisories/GHSA-3rpf-frgx-xq34
- https://nvd.nist.gov/vuln/detail/CVE-2026-63380
- https://github.com/libevent/libevent/commit/825c18bd99f556b59d61200523237f264d5cc734
