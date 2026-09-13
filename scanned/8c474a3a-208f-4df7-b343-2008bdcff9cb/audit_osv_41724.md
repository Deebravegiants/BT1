# [H] Libevent: Unbounded memory accumulation in WebSocket server via fragmented frames

## Summary
Severity: High
Advisory: CVE-2026-63495
Aliases: GHSA-qx89-wf2v-vgmx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-63495
Type: osv

## Details
Libevent is an event notification library. From 2.2.0-alpha-dev until 2.2.2-alpha, the libevent WebSocket server in ws.c accumulates fragmented frames in evws->incomplete_frames without enforcing a total message-size limit. An unauthenticated remote client can repeatedly send fragmented WebSocket frames below WS_MAX_RECV_FRAME_SZ with FIN=0, causing the evbuffer to grow without bound until the process or host exhausts memory. This issue is fixed in version 2.2.2-alpha.

## References
- https://github.com/libevent/libevent/releases/tag/release-2.2.2-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63495.json
- https://github.com/libevent/libevent/security/advisories/GHSA-qx89-wf2v-vgmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-63495
- https://github.com/libevent/libevent/commit/291c4d1cd75695e898030ebd5c4ddf26c094077b
