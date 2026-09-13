# [M] Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-8wch-9gcg-v2pr
CVE: CVE-2009-2902
CWE: CWE-22
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-8wch-9gcg-v2pr
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0 <5.5.29
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.24

## Details
Directory traversal vulnerability in Apache Tomcat 5.5.0 through 5.5.28 and 6.0.0 through 6.0.20 allows remote attackers to delete work-directory files via directory traversal sequences in a WAR filename, as demonstrated by the ...war filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-2902
- https://github.com/apache/tomcat/commit/3e1010b1a2f648581fac3d68afbf18f2979f6bf6
- https://github.com/apache/tomcat55/commit/0299cb724ea71f304d54adfcdb950f59b01fb421
- https://web.archive.org/web/20150308000602/http://www.securityfocus.com/archive/1/509150/100/0/threaded
- https://web.archive.org/web/20140515000000*/http://secunia.com/advisories/57126
- https://web.archive.org/web/20121211195847/http://www.securityfocus.com/bid/37945
- https://web.archive.org/web/20121211115829/http://securitytracker.com/id?1023504
- https://web.archive.org/web/20111119150528/http://www.securityfocus.com/archive/1/516397/100/0/threaded
- https://web.archive.org/web/20110601000000*/http://secunia.com/advisories/40330
- https://web.archive.org/web/20110529135656/http://secunia.com/advisories/38541
- https://web.archive.org/web/20110213053623/https://secunia.com/advisories/43310
- https://web.archive.org/web/20100601000000*/http://secunia.com/advisories/40813
- https://web.archive.org/web/20100412065745/http://secunia.com/advisories/39317
- https://web.archive.org/web/20100329100145/http://secunia.com/advisories/38687
- https://web.archive.org/web/20100127190258/http://secunia.com/advisories/38316
- https://web.archive.org/web/20100127015355/http://secunia.com/advisories/38346
- https://support.hpe.com/hpesc/public/docDisplay?docId=c02241113
- https://support.apple.com/kb/HT4077
- https://oval.cisecurity.org/repository/search/definition/oval:org.mitre.oval:def:7092
- https://oval.cisecurity.org/repository/search/definition/oval:org.mitre.oval:def:19431
