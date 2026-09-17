# [H] Apache Struts Access Control Redirect

## Summary
Severity: High
Advisory: GHSA-vq79-mgpx-2wx4
CVE: CVE-2016-4431
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vq79-mgpx-2wx4
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts-parent` — affected >=2.3.20 <2.3.29

## Details
Apache Struts 2 2.3.20 through 2.3.28.1 allows remote attackers to bypass intended access restrictions and conduct redirection attacks by leveraging a default method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4431
- https://github.com/apache/struts/commit/eccc31ebce5430f9e91b9684c63eaaf885e603f9
- https://bugzilla.redhat.com/show_bug.cgi?id=1348252
- https://github.com/apache/struts
- https://struts.apache.org/docs/s2-040.html
- https://web.archive.org/web/20210123145002/http://www.securityfocus.com/bid/91284
- http://jvn.jp/en/jp/JVN45093481/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2016-000113
- http://www-01.ibm.com/support/docview.wss?uid=ssg1S1009282
- http://www-01.ibm.com/support/docview.wss?uid=swg21987854
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
