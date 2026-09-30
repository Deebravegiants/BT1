# [H] Apache Ranger allows users to bypass intended access restrictions via direct access to module URLs

## Summary
Severity: High
Advisory: GHSA-7ccv-hhvc-62hg
CVE: CVE-2015-0266
CWE: CWE-639, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7ccv-hhvc-62hg
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0 <0.5.0

## Details
The Policy Admin Tool in Apache Ranger before 0.5.0 allows remote authenticated users to bypass intended access restrictions via direct access to module URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0266
- https://cwiki.apache.org/confluence/display/RANGER/Vulnerabilities+found+in+Ranger
- https://github.com/apache/ranger
- https://mail-archives.apache.org/mod_mbox/ranger-dev/201508.mbox/%3CD1E7EC30.9D53F%25vel%40apache.org%3E
- https://mail-archives.apache.org/mod_mbox/ranger-dev/201508.mbox/%3CD1E7EC30.9D53F%25vel@apache.org%3E
- https://web.archive.org/web/20200228073944/http://www.securityfocus.com/bid/76221
- http://www.slideshare.net/wojdwo/big-problems-with-big-data-hadoop-interfaces-security
