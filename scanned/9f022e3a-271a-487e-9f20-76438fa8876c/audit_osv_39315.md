# [M] MyBB: Insufficient permission check for calendar event move

## Summary
Severity: Medium
Advisory: CVE-2026-45122
Aliases: GHSA-839m-gpw8-59j4
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-45122
Type: osv

## Details
MyBB is free and open source forum software. Prior to 1.8.40, the calendar module does not validate moderation permissions for the destination calendar when moving events. A user with moderation permission for the source calendar can move an event to a calendar where the user has only viewing permission because the do_move action in calendar.php does not check canmoderateevents for the target calendar. The uniquely identifying implementation details include calendar event move, source calendar moderation permission, and destination calendar viewing permission. This issue is fixed in version 1.8.40.

## References
- https://github.com/mybb/mybb/releases/tag/mybb_1840
- https://mybb.com/versions/1.8.40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45122.json
- https://github.com/mybb/mybb/security/advisories/GHSA-839m-gpw8-59j4
- https://nvd.nist.gov/vuln/detail/CVE-2026-45122
- https://github.com/mybb/mybb/commit/86ed2058e7f9a2c14828e731f684e997f9bb220c
