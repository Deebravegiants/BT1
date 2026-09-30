# [C] Apache OpenMeetings missing authentication and can allow user impersonation 

## Summary
Severity: Critical
Advisory: GHSA-3r48-3m8r-4r9w
CVE: CVE-2023-28326
CWE: CWE-306
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-28
Source: https://github.com/advisories/GHSA-3r48-3m8r-4r9w
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=2.0.0 <7.0.0

## Details
The Apache Software Foundation's OpenMeetings from 2.0.0 before 7.0.0 is missing authentication on meeting invitation URLs. An invitation URL contains a hash that automatically logs in as the invited user. An unauthorized user could obtain this URL and log in to the meeting as an invited user, in effect elevating their privileges in the meeting room. OpenMeetings 7.0.0 disables this option if a contact is not selected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28326
- https://github.com/apache/openmeetings/commit/1fb71af36
- https://github.com/apache/openmeetings
- https://lists.apache.org/thread/r9vn12dp5yofn1h3wd5x4h7c3vmmr5d9
