# [H] Apache InLong vulnerable to JDBC Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-gpqq-59rp-3c3w
CVE: CVE-2023-27296
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-27
Source: https://github.com/advisories/GHSA-gpqq-59rp-3c3w
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:inlong-manager` — affected >=1.1.0 <1.6.0

## Details
Apache InLong versions from 1.1.0 through 1.5.0 are vulnerable to Java Database Connectivity (JDBC) deserialization of untrusted data from the MySQL JDBC URL in MySQLDataNode. It could be triggered by authenticated users of InLong. This has been patched in version 1.6.0. Users are advised to upgrade to Apache InLong's latest version or cherry-pick the [patch](https://github.com/apache/inlong/pull/7422) to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27296
- https://github.com/apache/inlong/pull/7422
- https://github.com/apache/inlong
- https://lists.apache.org/thread/xbvtjw9bwzgbo9fp1by8o3p49nf59xzt
- https://programmer.help/blogs/jdbc-deserialization-vulnerability-learning.html
