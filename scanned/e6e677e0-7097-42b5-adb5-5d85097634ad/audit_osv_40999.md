# [H] 9router: Reverse proxy locality collapse allows unauthenticated access to 9router /v1 APIs

## Summary
Severity: High
Advisory: CVE-2026-56675
Aliases: GHSA-x5c9-v98j-722r
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-56675
Type: osv

## Details
9Router is an AI router & token saver. Prior to 0.5.2, 9router treats loopback requests as trusted and allows /v1/* access without an API key, so a same-host reverse proxy that forwards public traffic to the backend through 127.0.0.1 causes src/dashboardGuard.js to misclassify external requests as local. A remote unauthenticated attacker can access /v1 APIs such as /v1/models and may abuse configured upstream provider credentials through /v1 proxy endpoints depending on enabled providers. This issue is fixed in version 0.5.2.

## References
- https://github.com/decolua/9router/releases/tag/v0.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56675.json
- https://github.com/decolua/9router/security/advisories/GHSA-x5c9-v98j-722r
- https://nvd.nist.gov/vuln/detail/CVE-2026-56675
- https://github.com/decolua/9router/commit/da667836cc7584bea0edd893de1d590c9ea279dc
