# [M] Apache OpenMeetings has an Improper Handling of Insufficient Privileges vulnerability

## Summary
Severity: Medium
Advisory: GHSA-78cg-fc6c-w44w
CVE: CVE-2026-33005
CWE: CWE-274
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-78cg-fc6c-w44w
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=3.10 <9.0.0

## Details
Sny registered user can query web service with their credentials and get files/sub-folders of any folder by ID (metadata only NOT contents). Metadata includes id, type, name and some other field. Full list of fields get be checked at FileItemDTO object.

This issue affects Apache OpenMeetings: from 3.10 before 9.0.0.

Users are recommended to upgrade to version 9.0.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33005
- https://github.com/apache/openmeetings
- https://lists.apache.org/thread/pttoprd628g3xr6lpp3bm1z8m3z8t4p7
- https://openmeetings.apache.org/openmeetings-db/apidocs/org.apache.openmeetings.db/org/apache/openmeetings/db/dto/file/FileItemDTO.html
- http://www.openwall.com/lists/oss-security/2026/04/09/10
