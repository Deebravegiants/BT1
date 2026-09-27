# [C] Apache Linkis Zip Slip issue

## Summary
Severity: Critical
Advisory: GHSA-pj5j-w7mw-w797
CVE: CVE-2023-27603
CWE: CWE-22, CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-pj5j-w7mw-w797
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis` — affected >=0 <1.3.2

## Details
In Apache Linkis <=1.3.1, due to the Manager module engineConn material upload does not check the zip path, This is a Zip Slip issue, which will lead to a potential RCE vulnerability.


We recommend users upgrade the version of Linkis to version 1.3.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27603
- https://github.com/apache/linkis
- https://lists.apache.org/thread/6n1vlvnyn441rm02zdqc0wnpckj8ltn8
- https://www.openwall.com/lists/oss-security/2023/04/10/2
