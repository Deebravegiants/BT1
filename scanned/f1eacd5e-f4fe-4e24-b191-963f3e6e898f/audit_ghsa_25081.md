# [M] Use of Hard-coded Cryptographic Key in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-6cr4-7c7p-p3xv
CVE: CVE-2011-5064
CWE: CWE-321
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-6cr4-7c7p-p3xv
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0 <5.5.34
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.33
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.12

## Details
DigestAuthenticator.java in the HTTP Digest Access Authentication implementation in Apache Tomcat 5.5.x before 5.5.34, 6.x before 6.0.33, and 7.x before 7.0.12 uses Catalina as the hard-coded server secret (aka private key), which makes it easier for remote attackers to bypass cryptographic protection mechanisms by leveraging knowledge of this string, a different vulnerability than CVE-2011-1184.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-5064
- https://github.com/apache/tomcat
- https://lists.apache.org/thread.html/06cfb634bc7bf37af7d8f760f118018746ad8efbd519c4b789ac9c2e@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5@%3Cdev.tomcat.apache.org%3E
- http://lists.opensuse.org/opensuse-security-announce/2012-02/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2012-02/msg00006.html
- http://marc.info/?l=bugtraq&m=139344343412337&w=2
- http://rhn.redhat.com/errata/RHSA-2012-0074.html
- http://rhn.redhat.com/errata/RHSA-2012-0075.html
- http://rhn.redhat.com/errata/RHSA-2012-0076.html
- http://secunia.com/advisories/57126
- http://svn.apache.org/viewvc?view=rev&rev=1087655
- http://svn.apache.org/viewvc?view=rev&rev=1158180
- http://svn.apache.org/viewvc?view=rev&rev=1159309
- http://tomcat.apache.org/security-5.html
- http://tomcat.apache.org/security-6.html
- http://tomcat.apache.org/security-7.html
- http://www.debian.org/security/2012/dsa-2401
