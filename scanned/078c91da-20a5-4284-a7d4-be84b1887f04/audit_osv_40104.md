# [C] FreeSWITCH: Pre-authentication heap buffer overflow in libesl `Content-Length` parsing

## Summary
Severity: Critical
Advisory: CVE-2026-49840
Aliases: GHSA-g597-9fgg-ghg9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-49840
Type: osv

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.11.1, esl_recv_event() parses Content-Length with atol() and passes the result straight to malloc(len + 1) with no sign or magnitude check. A malicious or man-in-the-middle ESL peer can send a frame with a negative Content-Length to corrupt the heap of, or crash, any process linked against libesl, before the client has authenticated to that peer. This issue has been patched in version 1.11.1.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49840.json
- https://github.com/signalwire/freeswitch/security/advisories/GHSA-g597-9fgg-ghg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-49840
