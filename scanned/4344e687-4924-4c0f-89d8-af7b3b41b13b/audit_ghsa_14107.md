# [H] Apache OpenMeetings Improper Authentication vulnerability

## Summary
Severity: High
Advisory: GHSA-v9rm-7rv9-r3fw
CVE: CVE-2023-29032
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-12
Source: https://github.com/advisories/GHSA-v9rm-7rv9-r3fw
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=3.1.3 <7.1.0

## Details
An attacker that has gained access to certain private information can use this to act as other user.

Vendor: The Apache Software Foundation

Versions Affected: Apache OpenMeetings from 3.1.3 before 7.1.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29032
- https://github.com/apache/openmeetings/commit/4e89e0ca076c83f26562f1146cf3e81ba0b16a7f
- https://github.com/apache/openmeetings
- https://issues.apache.org/jira/browse/OPENMEETINGS-2764
- https://lists.apache.org/thread/j2d6mg3rzcphfd8vvvk09d8p4o9lvnqp
