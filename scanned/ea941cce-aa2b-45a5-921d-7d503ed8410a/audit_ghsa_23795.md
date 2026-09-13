# [H] Apache Sentry may allow attacker to access/remove data from Sentry protected table

## Summary
Severity: High
Advisory: GHSA-6xhj-p29v-82j8
CVE: CVE-2018-8028
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6xhj-p29v-82j8
Type: github-advisory

## Affected
- Maven: `org.apache.sentry:sentry` — affected >=0 <2.0.1

## Details
An authenticated user can execute ALTER TABLE EXCHANGE PARTITIONS without being authorized by Apache Sentry before 2.0.1. This can allow an attacker unauthorized access to the partitioned data of a Sentry protected table and can allow an attacker to remove data from a Sentry protected table.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8028
- https://cwiki.apache.org/confluence/display/SENTRY/Vulnerabilities+found+in+Apache+Sentry
- https://github.com/apache/sentry
