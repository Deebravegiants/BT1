# [H] Apache Atlas: zip path traversal in import functionality

## Summary
Severity: High
Advisory: GHSA-p782-4j23-xqcg
CVE: CVE-2022-34271
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-p782-4j23-xqcg
Type: github-advisory

## Affected
- Maven: `org.apache.atlas:apache-atlas` — affected >=0.8.4 <2.3.0

## Details
A vulnerability in import module of Apache Atlas allows an authenticated user to write to web server filesystem. This issue affects Apache Atlas versions from 0.8.4 to 2.2.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34271
- https://github.com/apache/atlas/commit/3415913d252597c24c6b5d19d315375a49e64152
- https://github.com/apache/atlas
- https://issues.apache.org/jira/browse/ATLAS-4622
- https://lists.apache.org/thread/0rqvcxo6brmos9w3lzfsdn2lsmlblpw3
