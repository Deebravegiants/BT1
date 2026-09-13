# [M] SQL Injection in Apache Kylin

## Summary
Severity: Medium
Advisory: GHSA-5429-pjww-7675
CVE: CVE-2021-36774
CWE: CWE-668, CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-5429-pjww-7675
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin` — affected >=0 <3.1.3

## Details
Apache Kylin allows users to read data from other database systems using JDBC. The MySQL JDBC driver supports certain properties, which, if left unmitigated, can allow an attacker to execute arbitrary code from a hacker-controlled malicious MySQL server within Kylin server processes. This issue affects Apache Kylin 2 version 2.6.6 and prior versions; Apache Kylin 3 version 3.1.2 and prior versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36774
- https://github.com/apache/kylin/pull/1646
- https://github.com/apache/kylin
- https://lists.apache.org/thread/lchpcvoolc6w8zc6vo1wstk8zbfqv2ow
- http://www.openwall.com/lists/oss-security/2022/01/06/5
