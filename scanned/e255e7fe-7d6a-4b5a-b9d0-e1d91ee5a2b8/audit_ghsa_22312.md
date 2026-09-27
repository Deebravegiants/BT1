# [M] Apache Ranger allows users to bypass intended access restrictions via the REST API

## Summary
Severity: Medium
Advisory: GHSA-qqg7-gcxw-gmj3
CVE: CVE-2015-5167
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qqg7-gcxw-gmj3
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0 <0.5.1

## Details
The Policy Admin Tool in Apache Ranger before 0.5.1 allows remote authenticated users to bypass intended access restrictions via the REST API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5167
- https://cwiki.apache.org/confluence/display/RANGER/Vulnerabilities+found+in+Ranger
- https://github.com/apache/ranger
- https://mail-archives.apache.org/mod_mbox/ranger-dev/201602.mbox/%3CD2D9A4C5.114ECA%25vel%40apache.org%3E
- https://mail-archives.apache.org/mod_mbox/ranger-dev/201602.mbox/%3CD2D9A4C5.114ECA%25vel@apache.org%3E
- https://web.archive.org/web/20200501000000*/http://www.securityfocus.com/bid/82871
