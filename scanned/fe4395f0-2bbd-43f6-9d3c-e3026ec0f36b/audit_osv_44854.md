# [M] Open WebUI: Any authenticated user can suppress calendar alerts instance-wide via a non-numeric alert value

## Summary
Severity: Medium
Advisory: CVE-2026-87012
Aliases: GHSA-v39v-59xw-j98g
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87012
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.9.0 until 0.11.1, backend/open_webui/models/calendar.py stored the calendar event meta.alert_minutes value without type validation and the shared upcoming-event scheduler compared that value numerically. An authenticated user with the calendar permission could store a non-numeric alert_minutes value that raised an exception and aborted the instance-wide alert pass, suppressing all users' reminders while the event remained in the lookahead window. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87012.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-v39v-59xw-j98g
- https://nvd.nist.gov/vuln/detail/CVE-2026-87012
- https://github.com/open-webui/open-webui/commit/abc69000b33b4894fbd97fc2c962139cf9a8d784
- https://github.com/open-webui/open-webui/pull/28790
