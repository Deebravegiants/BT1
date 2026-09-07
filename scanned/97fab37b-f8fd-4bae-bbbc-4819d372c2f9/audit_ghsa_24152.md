# [M] Apache Struts vulnerable to possible DoS attack when using URLValidator

## Summary
Severity: Medium
Advisory: GHSA-xg75-68x3-7p3q
CVE: CVE-2016-4465
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xg75-68x3-7p3q
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.3.20 <2.3.29
- Maven: `org.apache.struts:struts2-core` — affected >=2.5.0 <2.5.13

## Details
The URLValidator class in Apache Struts 2 2.3.20 through 2.3.28.1 and 2.5.x before 2.5.13 allows remote attackers to cause a denial of service via a null value for a URL field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4465
- https://github.com/apache/struts/commit/a0fdca138feec2c2e94eb75ca1f8b76678b4d152
- https://github.com/apache/struts/commit/eccc31ebce5430f9e91b9684c63eaaf885e603f9
- https://bugzilla.redhat.com/show_bug.cgi?id=1348253
- https://github.com/apache/struts
- https://struts.apache.org/docs/s2-041.html
- http://jvn.jp/en/jp/JVN12352818/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2016-000114
- http://www-01.ibm.com/support/docview.wss?uid=swg21987854
