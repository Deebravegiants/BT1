# [M] MyBB: Mod CP report resolution missing authorization

## Summary
Severity: Medium
Advisory: CVE-2026-45124
Aliases: GHSA-gfxj-g7w6-6w4v
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-45124
Type: osv

## Details
MyBB is free and open source forum software. Prior to 1.8.40, the Mod CP Report Center does not check permissions consistently, allowing moderators without report-management permission to mark reports as resolved. The modcp.php?action=do_reports Mark Selected as Read handler is reachable with canmodcp even without canmanagereportedcontent or canmanagereportedposts. When no forums are in scope, $flist_reports is empty and the UPDATE mybb_reportedcontent query executes without the expected permission-based limitation. This issue is fixed in version 1.8.40.

## References
- https://github.com/mybb/mybb/releases/tag/mybb_1840
- https://mybb.com/versions/1.8.40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45124.json
- https://github.com/mybb/mybb/security/advisories/GHSA-gfxj-g7w6-6w4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-45124
- https://github.com/mybb/mybb/commit/5cda5f6d183bc2cac24f0533e8d3060a9a46cc42
