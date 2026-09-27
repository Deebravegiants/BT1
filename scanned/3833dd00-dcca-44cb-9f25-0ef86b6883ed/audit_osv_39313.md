# [M] MyBB: Insufficient authorization for private calendar events

## Summary
Severity: Medium
Advisory: CVE-2026-45120
Aliases: GHSA-c2hm-g9w6-pv6x
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-45120
Type: osv

## Details
MyBB is free and open source forum software. Prior to 1.8.40, the calendar module does not verify private event status consistently, allowing users with viewing and moderation permissions to access and moderate private events. The private-event check used by get_events() in inc/functions_calendar.php and the event action is missing from the remaining calendar.php actions, despite the limited-access behavior described in inc/languages/english/calendar.lang.php. This issue is fixed in version 1.8.40.

## References
- https://github.com/mybb/mybb/releases/tag/mybb_1840
- https://mybb.com/versions/1.8.40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45120.json
- https://github.com/mybb/mybb/security/advisories/GHSA-c2hm-g9w6-pv6x
- https://nvd.nist.gov/vuln/detail/CVE-2026-45120
- https://github.com/mybb/mybb/commit/c077e6c29755187c4df78a1e674dd61bc55701b3
