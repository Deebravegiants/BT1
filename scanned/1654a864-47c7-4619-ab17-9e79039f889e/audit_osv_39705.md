# [H] BigBlueButton: Blind SQL Injection AUTH (Moderator)

## Summary
Severity: High
Advisory: CVE-2026-46682
Aliases: GHSA-gfv2-46v4-jvw5
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-46682
Type: osv

## Details
BigBlueButton is an open-source virtual classroom. Prior to 3.0.23, BigBlueButton allowed authenticated moderators to inject SQL through the meetingId and userId values used by refreshBreakoutRoomsVisibleForUsers in akka-bbb-apps/src/main/scala/org/bigbluebutton/core/db/BreakoutRoomUserDAO.scala. The method interpolated those values into breakout room visibility queries, allowing arbitrary SQL execution against the application database. This issue is fixed in version 3.0.23.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v3.0.23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46682.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-gfv2-46v4-jvw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-46682
- https://github.com/bigbluebutton/bigbluebutton/commit/3365e340e0c102de0f8ea007c05053b562b6fa2b
