# [M] Checkmate: Regular Expression Denial of Service (ReDoS) via User-Controlled Regex in Monitor Advanced Matching

## Summary
Severity: Medium
Advisory: CVE-2026-70656
Aliases: GHSA-4c6j-p2cv-wf56
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-70656
Type: osv

## Details
Checkmate is an open-source, self-hosted tool designed to track and monitor server hardware, uptime, response times, and incidents in real-time with beautiful visualizations. From 3.5.1 until 3.9.2, an authenticated admin or superadmin can set matchMethod to regex and place a malicious expression in the expectedValue field for advanced HTTP monitor matching. server/src/api/validation/monitorValidation.ts accepts the expression, and server/src/service/network/AdvancedMatcher.ts synchronously evaluates it against an attacker-controlled HTTP response body on the Node.js main event loop without a timeout or worker isolation, allowing catastrophic backtracking to freeze API endpoints, monitor checks, and WebSocket connections for all users. This issue is fixed in version 3.9.2.

## References
- https://github.com/bluewave-labs/Checkmate/releases/tag/v3.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70656.json
- https://github.com/bluewave-labs/Checkmate/security/advisories/GHSA-4c6j-p2cv-wf56
- https://nvd.nist.gov/vuln/detail/CVE-2026-70656
- https://github.com/bluewave-labs/Checkmate/commit/0df71d6356c87c747e0b796b0c34e33f2a5203fa
- https://github.com/bluewave-labs/Checkmate/commit/adba25269c455878bf8065bc28cfe5d74e58692f
- https://github.com/bluewave-labs/Checkmate/commit/d5ec2936ad77ab773529057b442a6eb55dd578eb
