# [H] Apache OpenMeetings vulnerable to remote code execution via null-bye injection

## Summary
Severity: High
Advisory: GHSA-mg5h-f3q8-c96g
CVE: CVE-2023-29246
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-12
Source: https://github.com/advisories/GHSA-mg5h-f3q8-c96g
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=2.0.0 <7.1.0

## Details
An attacker who has gained access to an admin account can perform RCE via null-byte injection

Vendor: The Apache Software Foundation

Versions Affected: Apache OpenMeetings from 2.0.0 before 7.1.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29246
- https://github.com/apache/openmeetings/commit/8e65a1344157b2898f2922d49a0bd2105687c4a5
- https://github.com/apache/openmeetings/commit/9f12a48994d0ad741ac140c52cbd2152f0d048d5
- https://github.com/apache/openmeetings/commit/f91ff1917027625f066a9007694a31d06e69df3a
- https://github.com/apache/openmeetings
- https://issues.apache.org/jira/browse/OPENMEETINGS-2765
- https://lists.apache.org/thread/230plvhbdx26m43b0sy942wlwt6kkmmr
