# [M] Apache Archiva subject to arbitrary directory deletion by users.

## Summary
Severity: Medium
Advisory: GHSA-xgq8-jq9w-77r5
CVE: CVE-2022-40309
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-xgq8-jq9w-77r5
Type: github-advisory

## Affected
- Maven: `org.apache.archiva:archiva-common` — affected >=0 <2.2.9

## Details
Apache Archiva prior to 2.2.9 allows an authenticated user to delete arbitrary directories. Users with write permissions to a repository can delete arbitrary directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40309
- https://github.com/apache/archiva
- https://lists.apache.org/thread/1odl4p85r96n27k577jk6ftrp19xfc27
- http://www.openwall.com/lists/oss-security/2022/11/15/3
