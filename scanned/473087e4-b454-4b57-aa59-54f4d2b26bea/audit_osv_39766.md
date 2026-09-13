# [M] MyBB: Buddy list corruption

## Summary
Severity: Medium
Advisory: CVE-2026-47245
Aliases: GHSA-w8gm-j57p-jqpc
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-47245
Type: osv

## Details
MyBB is free and open source forum software. Prior to 1.8.40, the User CP Buddy/Ignore List component does not validate reciprocal buddy-list updates correctly. The usercp.php?action=do_editlists delete handler removes the selected entry from the acting user's list and then updates mybb_users.buddylist for the target account. The reciprocal update searches for the deleted target UID instead of the acting user's UID and uses the unchecked array_search() return value as an array key. A false result can be converted to index 0, removing the target account's first stored buddy while leaving the actual reciprocal entry unchanged. The uniquely identifying implementation details include false converted to index 0. This issue is fixed in version 1.8.40.

## References
- https://github.com/mybb/mybb/releases/tag/mybb_1840
- https://mybb.com/versions/1.8.40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47245.json
- https://github.com/mybb/mybb/security/advisories/GHSA-w8gm-j57p-jqpc
- https://nvd.nist.gov/vuln/detail/CVE-2026-47245
- https://github.com/mybb/mybb/commit/0557718f27503034fb1c2768729a2fb8239bba65
