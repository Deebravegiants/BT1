# [C] FreeRDP: Heap-buffer-overflow write in TS Gateway RPC fragment receive due to uncapped bind_ack max_xmit_frag

## Summary
Severity: Critical
Advisory: CVE-2026-55193
Aliases: GHSA-7rp4-66mc-j9vx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-55193
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.27.0, FreeRDP clients using TS Gateway accept a server-controlled max_xmit_frag value in libfreerdp/core/gateway/rpc_bind.c without bounding it to the 4088-byte ReceiveFragment allocation. A malicious gateway can advertise 65535 and then send a response fragment of the same length, causing rpc_channel_read in libfreerdp/core/gateway/rpc.c to write up to 65535 bytes into the smaller ReceiveFragment buffer. This can crash the client and may permit code execution through attacker-controlled heap corruption. This issue is fixed in version 3.27.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55193.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-7rp4-66mc-j9vx
- https://nvd.nist.gov/vuln/detail/CVE-2026-55193
- https://github.com/FreeRDP/FreeRDP/commit/a863ef1cf1cdabf9019280e5658f806e73bb50e8
- https://github.com/FreeRDP/FreeRDP/pull/12873
