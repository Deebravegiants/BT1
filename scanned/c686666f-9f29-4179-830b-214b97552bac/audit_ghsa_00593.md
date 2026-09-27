# [M] Moderate severity vulnerability that affects org.apache.hive:hive-jdbc

## Summary
Severity: Medium
Advisory: GHSA-jmf4-pq78-f8vj
CVE: CVE-2018-1314
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-jmf4-pq78-f8vj
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive-jdbc` — affected >=0 <2.3.4
- Maven: `org.apache.hive:hive-jdbc` — affected >=3.0.0 <3.1.1

## Details
In Apache Hive 2.3.3, 3.1.0 and earlier, Hive "EXPLAIN" operation does not check for necessary authorization of involved entities in a query. An unauthorized user can do "EXPLAIN" on arbitrary table or view and expose table metadata and statistics.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1314
- https://github.com/advisories/GHSA-jmf4-pq78-f8vj
- https://lists.apache.org/thread.html/3da47dbcbf09697387f29d2f1aed970523b6b334d93afd3cced23727@%3Cdev.hive.apache.org%3E
- http://www.securityfocus.com/bid/105884
