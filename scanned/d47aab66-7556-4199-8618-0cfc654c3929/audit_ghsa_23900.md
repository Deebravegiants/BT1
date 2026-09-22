# [M] Apache OpenMeetings may allow authenticated attacker to deny service for privileged users

## Summary
Severity: Medium
Advisory: GHSA-cv9j-7q4x-v2g2
CVE: CVE-2018-1286
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cv9j-7q4x-v2g2
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=3.0.0 <4.0.2

## Details
In Apache OpenMeetings 3.0.0 - 4.0.1, CRUD operations on privileged users are not password protected allowing an authenticated attacker to deny service for privileged users. The issue is fixed in version 4.0.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1286
- https://github.com/apache/openmeetings
- https://lists.apache.org/thread.html/dc2151baa5301bae773603cede0d62c21ee28588dd06e5e9253c13a8@%3Cuser.openmeetings.apache.org%3E
