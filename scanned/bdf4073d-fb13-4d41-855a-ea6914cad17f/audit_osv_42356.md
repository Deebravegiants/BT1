# [M] FreeRDP before 3.29.0 Use-After-Free via async message proxy

## Summary
Severity: Medium
Advisory: CVE-2026-67300
Aliases: GHSA-33gg-h66j-3697
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67300
Type: osv

## Details
FreeRDP before 3.29.0 contains client-side heap use-after-free vulnerabilities in the async update message proxy for RAIL WINDOW_STATE_ORDER and NOTIFY_ICON_STATE_ORDER when AsyncUpdate is enabled. When a malicious or compromised RDP server sends crafted update orders, the message proxy shallow-copies structures containing nested parser-owned pointers (e.g., titleInfo.string, windowRects, visibilityRects, icon buffers). The parser frees those nested buffers after the callback returns, so the queued async message later dispatches stale pointers, potentially causing memory corruption or a client crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67300.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-33gg-h66j-3697
- https://nvd.nist.gov/vuln/detail/CVE-2026-67300
- https://www.vulncheck.com/advisories/freerdp-before-use-after-free-via-async-message-proxy
- https://github.com/FreeRDP/FreeRDP/commit/5370fb26fbf034ecd11d3026b6ad639b5fff493f
