# [M] Mockoon: Path traversal in templated `filePath` lets a request escape the served directory (prefix-only base check)

## Summary
Severity: Medium
Advisory: CVE-2026-59149
Aliases: GHSA-8wqc-v2q8-vff2
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-59149
Type: osv

## Details
Mockoon provides way to design and run mock APIs. Prior to 9.7.0, a FILE response whose filePath embeds request data is confined by getSafeFilePath in packages/commons-server/src/libs/server/server.ts with resolvedPath.startsWith(staticBaseDir). That prefix test has no path-separator boundary, so a ../-escaped path whose absolute form string-prefixes the base directory passes, allowing an unauthenticated client to read files from sibling paths outside the served directory through HTTP sendFile, WebSocket, or callbacks. This issue is fixed in version 9.7.0.

## References
- https://github.com/mockoon/mockoon/releases/tag/v9.7.0
- https://mockoon.com/releases/9.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59149.json
- https://github.com/mockoon/mockoon/security/advisories/GHSA-8wqc-v2q8-vff2
- https://nvd.nist.gov/vuln/detail/CVE-2026-59149
- https://github.com/mockoon/mockoon/commit/b42bdfb7f82e83f0e81bea8e6fe41adf5ec82585
- https://github.com/mockoon/mockoon/pull/2255
