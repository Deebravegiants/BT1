# [M] Denial of service in Apache Xerces2

## Summary
Severity: Medium
Advisory: GHSA-334p-wv2m-w3vp
CVE: CVE-2009-2625
Ecosystem: Maven
Published: 2020-06-15
Source: https://github.com/advisories/GHSA-334p-wv2m-w3vp
Type: github-advisory

## Affected
- Maven: `xerces:xercesImpl` — affected >=0 <2.10.0

## Details
XMLScanner.java in Apache Xerces2 Java, as used in Sun Java Runtime Environment (JRE) in JDK and JRE 6 before Update 15 and JDK and JRE 5.0 before Update 20, and in other products, allows remote attackers to cause a denial of service (infinite loop and application hang) via malformed XML input, as demonstrated by the Codenomicon XML fuzzing framework.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-2625
- https://github.com/apache/xerces2-j/commit/0bdf77af1d4fd26ec2e630fb6d12e2dfa77bc12b
- https://bugzilla.redhat.com/show_bug.cgi?id=512921
- https://lists.apache.org/thread.html/r204ba2a9ea750f38d789d2bb429cc0925ad6133deea7cbc3001d96b5@%3Csolr-user.lucene.apache.org%3E
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A8520
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A9356
- https://rhn.redhat.com/errata/RHSA-2009-1199.html
- https://rhn.redhat.com/errata/RHSA-2009-1200.html
- https://rhn.redhat.com/errata/RHSA-2009-1201.html
- https://rhn.redhat.com/errata/RHSA-2009-1636.html
- https://rhn.redhat.com/errata/RHSA-2009-1637.html
- https://rhn.redhat.com/errata/RHSA-2009-1649.html
- https://rhn.redhat.com/errata/RHSA-2009-1650.html
- https://snyk.io/vuln/SNYK-JAVA-XERCES-32014
- https://www.redhat.com/archives/fedora-package-announce/2009-August/msg00310.html
- https://www.redhat.com/archives/fedora-package-announce/2009-August/msg00325.html
- http://lists.apple.com/archives/security-announce/2009/Sep/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2009-10/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2009-10/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2009-11/msg00002.html
