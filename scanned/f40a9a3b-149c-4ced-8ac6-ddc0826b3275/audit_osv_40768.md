# [C] FreeRDPHeap-buffer-overflow write in TS Gateway RPC RESPONSE reassembly due to alloc_hint capacity mismatch

## Summary
Severity: Critical
Advisory: CVE-2026-55194
Aliases: GHSA-9gxm-3mf5-f5cx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-55194
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.27.0, rpc_client_recv_fragment in libfreerdp/core/gateway/rpc_client.c ensures the response reassembly stream capacity using only the server-declared alloc_hint rather than the actual StubLength about to be written. A malicious TS Gateway can send a PTYPE_RESPONSE with a small alloc_hint and a much larger frag_length, causing Stream_Write to copy attacker-controlled stub data beyond the 4096-byte pdu->s buffer. This can crash the client and may permit code execution through heap corruption. This issue is fixed in version 3.27.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55194.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-9gxm-3mf5-f5cx
- https://nvd.nist.gov/vuln/detail/CVE-2026-55194
- https://github.com/FreeRDP/FreeRDP/commit/9f2da52c2341cc14a96ad12e69c5b83d0bcd8b5a
- https://github.com/FreeRDP/FreeRDP/pull/12873
