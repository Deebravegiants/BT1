# [C] Apache Cocoon SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-8v4w-jr33-4rh3
CVE: CVE-2022-45135
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-30
Source: https://github.com/advisories/GHSA-8v4w-jr33-4rh3
Type: github-advisory

## Affected
- Maven: `org.apache.cocoon:cocoon` — affected >=2.2.0 <2.3.0

## Details
Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') vulnerability in Apache Cocoon. This issue affects Apache Cocoon: from 2.2.0 before 2.3.0.

Users are recommended to upgrade to version 2.3.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45135
- https://github.com/apache/cocoon
- https://lists.apache.org/thread/lsvd1hmr2t2q823x21d5ygzgbj9jpvjp
- http://www.openwall.com/lists/oss-security/2023/11/30/3
