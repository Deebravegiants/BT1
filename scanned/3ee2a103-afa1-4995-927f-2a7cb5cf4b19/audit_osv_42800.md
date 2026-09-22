# [M] stream-json: pick/ignore/filter/replace filters are O(depth²) on nested input — small crafted JSON blocks the event loop for seconds→minutes (DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-71429
Aliases: GHSA-528h-pc64-c93x
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-71429
Type: osv

## Details
stream-json is a micro-library of stream components for processing JSON and JSONC with a minimal memory footprint. Prior to 3.5.0, the path filters pick, ignore, filter, and replace in src/core/filters/filter-base.js recompute the full path string from the nesting stack for every checkable token. Because the stack length equals the current nesting depth and a checkable token is emitted at every level, a depth D document costs O(D²) rather than O(D) to process. The issue is triggered by nesting depth rather than byte volume, including the documented pick({filter: 'data'}) traversal-until-match path, so an application that sends untrusted JSON through a string or RegExp filter can block the Node.js event loop and cause denial of service with a small deeply nested document. The streamArray, streamObject, and streamValues streamers are not affected because they use the constant-time asm.depth getter. This issue is fixed in version 3.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71429.json
- https://github.com/uhop/stream-json/security/advisories/GHSA-528h-pc64-c93x
- https://nvd.nist.gov/vuln/detail/CVE-2026-71429
- https://github.com/uhop/stream-json/commit/a869fb98aaef9225556f49901a8f55954ff856e6
