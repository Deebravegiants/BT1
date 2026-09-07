# [C] Apache OpenMeetings vulnerable to Deserialization of Untrusted Data 

## Summary
Severity: Critical
Advisory: GHSA-mjf9-4pcv-vfg7
CVE: CVE-2024-54676
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-08
Source: https://github.com/advisories/GHSA-mjf9-4pcv-vfg7
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=2.1.0 <8.0.0

## Details
Vendor: The Apache Software Foundation

Versions Affected: Apache OpenMeetings from 2.1.0 before 8.0.0

Description: Default clustering instructions at  https://openmeetings.apache.org/Clustering.html  doesn't specify white/black lists for OpenJPA this leads to possible deserialisation of untrusted data.
Users are recommended to upgrade to version 8.0.0 and update their startup scripts to include the relevant 'openjpa.serialization.class.blacklist' and 'openjpa.serialization.class.whitelist' configurations as shown in the documentation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-54676
- https://github.com/apache/openmeetings/commit/1c3426c6d3abbd984a3c01a61decf1242ea38923
- https://github.com/apache/openmeetings
- https://issues.apache.org/jira/browse/OPENMEETINGS-2787
- https://lists.apache.org/thread/o0k05jxrt5tp4nm45lj14yfjxmg67m95
- http://www.openwall.com/lists/oss-security/2025/01/08/1
