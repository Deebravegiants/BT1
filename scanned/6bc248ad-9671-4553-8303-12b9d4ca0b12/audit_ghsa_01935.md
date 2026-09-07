# [H] Uncontrolled Resource Consumption in Apache OpenMeetings server

## Summary
Severity: High
Advisory: GHSA-px9f-597f-wmcf
CVE: CVE-2021-27576
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-px9f-597f-wmcf
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=4.0.0 <6.0.0

## Details
If was found that the NetTest web service can be used to overload the bandwidth of a Apache OpenMeetings server. This issue was addressed in Apache OpenMeetings 6.0.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27576
- https://github.com/apache/openmeetings/commit/060a3114ad759931aeb42cd9afa9d1ebb39d3075
- https://github.com/apache/openmeetings/commit/afe26c950b127776f2dfe920abff41a584874de8
- https://github.com/apache/openmeetings/commit/cbdfd2f9731a8fe3daa9b4adf5da4a063fde161d
- https://issues.apache.org/jira/browse/OPENMEETINGS-2551
- https://lists.apache.org/thread.html/r9bb615bd70a0197368f5f3ffc887162686caeb0b5fc30592a7a871e9%40%3Cuser.openmeetings.apache.org%3E
- https://openmeetings.apache.org/security.html#cve-2021-27576---apache-openmeetings-bandwidth-can
