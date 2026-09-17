# [H] XML External Entity Reference (XXE) in the XML Format Plugin in Apache Drill

## Summary
Severity: High
Advisory: GHSA-v62g-jwj9-rfvx
CVE: CVE-2023-48362
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-24
Source: https://github.com/advisories/GHSA-v62g-jwj9-rfvx
Type: github-advisory

## Affected
- Maven: `org.apache.drill.exec:drill-java-exec` — affected >=1.19.0 <1.21.2

## Details
XXE in the XML Format Plugin in Apache Drill version 1.19.0 and greater allows a user to read any file on a remote file system or execute commands via a malicious XML file. Users are recommended to upgrade to version 1.21.2, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48362
- https://github.com/apache/drill/commit/0e88b7a5101d24c561a2a3efb12d7a3b3f7933f3
- https://github.com/apache/drill
- https://issues.apache.org/jira/browse/DRILL-8461
- https://lists.apache.org/thread/9tt0q4bdjwgw0dz0l9knqxjnpb5y6zsl
- http://www.openwall.com/lists/oss-security/2024/07/24/3
