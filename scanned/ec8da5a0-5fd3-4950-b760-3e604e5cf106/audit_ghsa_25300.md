# [H] Missing XML Validation in Apache Xerces2

## Summary
Severity: High
Advisory: GHSA-7j4h-8wpf-rqfh
CVE: CVE-2013-4002
CWE: CWE-112
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7j4h-8wpf-rqfh
Type: github-advisory

## Affected
- Maven: `xerces:xercesImpl` — affected >=0 <2.12.0

## Details
XMLscanner.java in Apache Xerces2 Java Parser before 2.12.0, as used in the Java Runtime Environment (JRE) in IBM Java 5.0 before 5.0 SR16-FP3, 6 before 6 SR14, 6.0.1 before 6.0.1 SR6, and 7 before 7 SR5 as well as Oracle Java SE 7u40 and earlier, Java SE 6u60 and earlier, Java SE 5.0u51 and earlier, JRockit R28.2.8 and earlier, JRockit R27.7.6 and earlier, Java SE Embedded 7u40 and earlier, and possibly other products allows remote attackers to cause a denial of service via vectors related to XML attribute names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4002
- https://github.com/apache/xerces2-j/commit/266e837852e0f0e3c8c1ad572b6fc4dbb4ded17
- https://access.redhat.com/errata/RHSA-2014:0414
- https://exchange.xforce.ibmcloud.com/vulnerabilities/85260
- https://github.com/apache/xerces2-j
- https://issues.apache.org/jira/browse/XERCESJ-1679
- https://lists.apache.org/thread.html/49dc6702104a86ecbb40292dcd329ce9ae4c32b74733199ecab14a73@%3Cj-users.xerces.apache.org%3E
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451@%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r204ba2a9ea750f38d789d2bb429cc0925ad6133deea7cbc3001d96b5@%3Csolr-user.lucene.apache.org%3E
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/technetwork/topics/security/cpuoct2013-1899837.html
- http://lists.apple.com/archives/security-announce/2013/Oct/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2013-07/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2013-07/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2013-07/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2013-07/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2013-08/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2013-08/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2013-11/msg00010.html
- http://lists.opensuse.org/opensuse-updates/2013-11/msg00023.html
