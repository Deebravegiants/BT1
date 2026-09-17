# [M] Apache OpenMeetings insufficient authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v93h-rwj8-78qh
CVE: CVE-2023-28936
CWE: CWE-697
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-v93h-rwj8-78qh
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-db` — affected >=2.0.0 <7.1.0

## Details
Attacker can access arbitrary recording/room

Vendor: The Apache Software Foundation

Versions Affected: Apache OpenMeetings from 2.0.0 before 7.1.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28936
- https://github.com/apache/openmeetings/commit/a28dea888fca1c5c3e0ce4c8a4c62f501aebe0cd
- https://github.com/apache/openmeetings
- https://issues.apache.org/jira/browse/OPENMEETINGS-2762
- https://lists.apache.org/thread/y6vng44c22ll221rtvsv208x1pbjmdoc
