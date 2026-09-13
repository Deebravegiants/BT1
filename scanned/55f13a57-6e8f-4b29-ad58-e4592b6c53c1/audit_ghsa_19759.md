# [M] Apache NiFi: Potential Insertion of MongoDB Password in Provenance Record

## Summary
Severity: Medium
Advisory: GHSA-35gq-cvrm-xf94
CVE: CVE-2025-27017
CWE: CWE-538
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-35gq-cvrm-xf94
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-mongodb-services` — affected >=1.13.0 <2.3.0

## Details
Apache NiFi 1.13.0 through 2.2.0 includes the username and password used to authenticate with MongoDB in the NiFi provenance events that MongoDB components generate during processing. An authorized user with read access to the provenance events of those processors may see the credentials information. Upgrading to Apache NiFi 2.3.0 is the recommended mitigation, which removes the credentials from provenance event records.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27017
- https://github.com/apache/nifi/commit/48d684500f6ad70f65bfd510db054590c5bc74a9
- https://github.com/apache/nifi
- https://issues.apache.org/jira/browse/NIFI-14272
- https://lists.apache.org/thread/d4n5474jkhp82dvnht13pjtlfx7bhn5q
- http://www.openwall.com/lists/oss-security/2025/03/11/1
