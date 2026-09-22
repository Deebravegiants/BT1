# [H] Apache OpenMeetings vulnerable to SQL injection

## Summary
Severity: High
Advisory: GHSA-335g-xcjh-ghc2
CVE: CVE-2017-7681
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-335g-xcjh-ghc2
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=1.0.0 <3.3.0

## Details
Apache OpenMeetings 1.0.0 is vulnerable to SQL injection. This allows authenticated users to modify the structure of the existing query and leak the structure of other queries being made by the application in the back-end. The issue is fixed in version 3.3.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7681
- https://github.com/apache/openmeetings
- http://markmail.org/message/j774dp5ro5xmkmg6
