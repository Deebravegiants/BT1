# [M] Apache Derby SQL Injection

## Summary
Severity: Medium
Advisory: GHSA-v7cq-pq7v-mh5v
CVE: CVE-2006-7217
CWE: CWE-89
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-v7cq-pq7v-mh5v
Type: github-advisory

## Affected
- Maven: `org.apache.derby:derby` — affected >=0 <10.2.1.6

## Details
Apache Derby before 10.2.1.6 does not determine schema privilege requirements during the DropSchemaNode bind phase, which allows remote authenticated users to execute arbitrary drop schema statements in SQL authorization mode.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-7217
- https://github.com/apache/derby/commit/28c633d82a776c90fd1cd835a0b66d1c8916d31a
- https://github.com/apache/derby
- https://svn.apache.org/viewvc?view=revision&revision=449869
- https://web.archive.org/web/20090406213028/http://www.novell.com/linux/security/advisories/suse_security_summary_report.html
- https://web.archive.org/web/20200301122517/https://issues.apache.org/jira/browse/DERBY-1858
- http://db.apache.org/derby/releases/release-10.2.1.6.html
