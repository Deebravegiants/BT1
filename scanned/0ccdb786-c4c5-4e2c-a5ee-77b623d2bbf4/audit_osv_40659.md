# [M] LibreChat: Incomplete Fix for CVE-2025-7105 — /api/convos/duplicate Lacks Rate Limiting Applied to /api/convos/fork

## Summary
Severity: Medium
Advisory: CVE-2026-54037
Aliases: GHSA-g445-9wq6-jf3v
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-54037
Type: osv

## Details
LibreChat is an enhanced ChatGPT clone that supports multiple AI providers. Prior to 0.8.4-rc1, the fix for CVE-2025-7105 added forkIpLimiter and forkUserLimiter rate limiters to POST /api/convos/fork to prevent rapid-fire conversation duplication. However, the POST /api/convos/duplicate endpoint — which is in the same file and performs the exact same expensive database operations — was not given any rate limiter. An authenticated user can bypass the CVE-2025-7105 fix by using /duplicate instead of /fork to exhaust server resources. This vulnerability is fixed in 0.8.4-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54037.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-g445-9wq6-jf3v
- https://nvd.nist.gov/vuln/detail/CVE-2026-54037
