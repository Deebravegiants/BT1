# [H] FreeSWITCH: Stack overflow in bundled cJSON parser via deeply nested JSON

## Summary
Severity: High
Advisory: CVE-2026-49847
Aliases: GHSA-2v74-pcgh-75wg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-49847
Type: osv

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.11.1, a single unauthenticated WebSocket frame containing a deeply nested JSON document crashes the FreeSWITCH process via stack overflow, terminating all calls and sessions on the host. The recursion drives the worker thread's stack pointer into the stack guard page, raising SIGSEGV from the kernel before any usable write primitive develops. This issue has been patched in version 1.11.1.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49847.json
- https://github.com/signalwire/freeswitch/security/advisories/GHSA-2v74-pcgh-75wg
- https://nvd.nist.gov/vuln/detail/CVE-2026-49847
