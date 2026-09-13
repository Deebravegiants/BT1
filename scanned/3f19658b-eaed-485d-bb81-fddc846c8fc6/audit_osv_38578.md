# [M] Next AI Draw.io: Unbounded HTTP Body — Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-40608
Aliases: GHSA-9q7h-wgfw-p378
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40608
Type: osv

## Details
Next AI Draw.io is a next.js web application that integrates AI capabilities with draw.io diagrams. Prior to 0.4.15, the embedded HTTP sidecar contains three POST handlers (/api/state, /api/restore, and /api/history-svg) that process incoming requests by accumulating the entire request body into a JavaScript string without any size limitations. Node.js buffers the entire payload in the V8 heap. Sending a sufficiently large body (e.g., 500 MiB or more) will exhaust the process heap memory, leading to an Out-of-Memory (OOM) error that crashes the MCP server. This vulnerability is fixed in 0.4.15.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40608.json
- https://github.com/DayuanJiang/next-ai-draw-io/security/advisories/GHSA-9q7h-wgfw-p378
- https://nvd.nist.gov/vuln/detail/CVE-2026-40608
- https://github.com/DayuanJiang/next-ai-draw-io/commit/31819f413cc4b329a1cb81e5fccd0cd98c1fd665
