# [M] OpenReplay: Authenticated ClickHouse SQL injection via session search

## Summary
Severity: Medium
Advisory: CVE-2026-57230
Aliases: GHSA-vxf8-j7jx-p65x
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:L)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-57230
Type: osv

## Details
OpenReplay is a self-hosted session replay suite. Prior to 1.27.0, the session search and analytics API in enterprise editions with multi-tenancy enabled built ClickHouse queries by inserting user input into the query string, including two positions that took input without escaping, allowing an authenticated member to read any ClickHouse table through blind boolean and time-based exfiltration and to break the project's session search for all viewers until the stored key is removed. This issue is fixed in version 1.27.0.

## References
- https://github.com/openreplay/openreplay/releases/tag/v1.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57230.json
- https://github.com/openreplay/openreplay/security/advisories/GHSA-vxf8-j7jx-p65x
- https://nvd.nist.gov/vuln/detail/CVE-2026-57230
- https://github.com/openreplay/openreplay/commit/ae8de6893250dd41175c6b2d312545c515fa5a16
- https://github.com/openreplay/openreplay/pull/4715
