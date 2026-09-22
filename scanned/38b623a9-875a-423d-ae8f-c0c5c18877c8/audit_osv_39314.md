# [M] MyBB: Insufficient permission check for calendar select

## Summary
Severity: Medium
Advisory: CVE-2026-45121
Aliases: GHSA-r25v-7pcm-q34p
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-45121
Type: osv

## Details
MyBB is free and open source forum software. Prior to 1.8.40, the calendar module does not check permissions consistently when listing calendars, allowing authenticated users to access titles of calendars that are otherwise inaccessible. The affected calendar-selection paths in calendar.php perform permission checks against an invalid calendar context before returning calendar titles. The uniquely identifying implementation details include titles of inaccessible calendars, and invalid calendar permission context. This issue is fixed in version 1.8.40.

## References
- https://github.com/mybb/mybb/releases/tag/mybb_1840
- https://mybb.com/versions/1.8.40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45121.json
- https://github.com/mybb/mybb/security/advisories/GHSA-r25v-7pcm-q34p
- https://nvd.nist.gov/vuln/detail/CVE-2026-45121
- https://github.com/mybb/mybb/commit/78e07fea34a6f6c326e668526bfb8e451c19e966
