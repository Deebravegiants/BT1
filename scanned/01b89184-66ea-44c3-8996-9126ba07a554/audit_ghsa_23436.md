# [M] Apache Tomcat Directory Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-ggx9-4728-588r
CVE: CVE-2009-2693
CWE: CWE-22
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-ggx9-4728-588r
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0 <5.5.29
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.24

## Details
Directory traversal vulnerability in Apache Tomcat 5.5.0 through 5.5.28 and 6.0.0 through 6.0.20 allows remote attackers to create or overwrite arbitrary files via a `..` (dot dot) in an entry in a WAR file, as demonstrated by a `../../bin/catalina.bat` entry.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-2693
- https://github.com/apache/tomcat/commit/3e1010b1a2f648581fac3d68afbf18f2979f6bf6
- https://github.com/apache/tomcat55/commit/0299cb724ea71f304d54adfcdb950f59b01fb421
- https://web.archive.org/web/20201206235536/http://www.securityfocus.com/archive/1/509148/100/0/threaded
- https://web.archive.org/web/20200516121700/http://www.securityfocus.com/archive/1/516397/100/0/threaded
- https://web.archive.org/web/20200229071135/http://www.securityfocus.com/bid/37944
- https://support.hpe.com/hpesc/public/docDisplay?docId=c02241113
- https://oval.cisecurity.org/repository/search/definition/oval:org.mitre.oval:def:7017
- https://oval.cisecurity.org/repository/search/definition/oval:org.mitre.oval:def:19355
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/06cfb634bc7bf37af7d8f760f118018746ad8efbd519c4b789ac9c2e@%3Cdev.tomcat.apache.org%3E
- https://github.com/apache/tomcat
- https://exchange.xforce.ibmcloud.com/vulnerabilities/55855
- https://access.redhat.com/errata/RHSA-2010:0582
- https://access.redhat.com/errata/RHSA-2010:0580
- https://access.redhat.com/errata/RHSA-2010:0119
- http://lists.apple.com/archives/security-announce/2010//Mar/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2010-04/msg00001.html
