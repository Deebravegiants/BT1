# [M] FreeRDP before 3.29.0 Use-After-Free via WindowIcon async message

## Summary
Severity: Medium
Advisory: CVE-2026-67299
Aliases: GHSA-34hq-hwjw-q8v3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67299
Type: osv

## Details
FreeRDP before 3.29.0 contains a client-side heap use-after-free in the async update message proxy for WINDOW_ICON_ORDER when AsyncUpdate is enabled (e.g. xfreerdp /async-update). In update_message_WindowIcon() a shallow CopyMemory() overwrites a freshly allocated lParam->iconInfo with the parser-owned windowIcon->iconInfo pointer. After the parser callback returns, update_recv_window_info_order() frees window_icon.iconInfo, but the queued async message still retains and later dispatches that stale pointer. A malicious or compromised RDP server sending a crafted RAIL Window Alternate Secondary Order with WINDOW_ORDER_ICON can trigger use-after-free, leading to memory corruption and client crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67299.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-34hq-hwjw-q8v3
- https://nvd.nist.gov/vuln/detail/CVE-2026-67299
- https://www.vulncheck.com/advisories/freerdp-before-use-after-free-via-windowicon-async-message
- https://github.com/FreeRDP/FreeRDP/commit/5370fb26fbf034ecd11d3026b6ad639b5fff493f
