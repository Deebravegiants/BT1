# [H] Apache OpenMeetings displays Tomcat version and detailed error stack trace

## Summary
Severity: High
Advisory: GHSA-4v67-wg88-37p9
CVE: CVE-2017-7683
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4v67-wg88-37p9
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=1.0.0 <3.3.0

## Details
Apache OpenMeetings 1.0.0 displays Tomcat version and detailed error stack trace, which is not secure. The issue is fixed in version 3.3.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7683
- https://github.com/apache/openmeetings
- http://markmail.org/message/hint6fp66lijqdvu
