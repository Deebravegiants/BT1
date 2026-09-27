# [M] JULI logging component in Apache Tomcat does not restrict certain permissions for web applications

## Summary
Severity: Medium
Advisory: GHSA-w65j-cmqc-37p2
CVE: CVE-2007-5342
CWE: CWE-284
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-w65j-cmqc-37p2
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-juli` — affected >=5.5.9
- Maven: `org.apache.tomcat:tomcat-juli` — affected >=6.0.0

## Details
The default catalina.policy in the JULI logging component in Apache Tomcat 5.5.9 through 5.5.25 and 6.0.0 through 6.0.15 does not restrict certain permissions for web applications, which allows attackers to modify logging configuration options and overwrite arbitrary files, as demonstrated by changing the (1) level, (2) directory, and (3) prefix attributes in the `org.apache.juli.FileHandler` handler.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-5342
- https://exchange.xforce.ibmcloud.com/vulnerabilities/39201
- https://github.com/apache/tomcat/tree/main/java/org/apache/juli
- https://lists.apache.org/thread.html/06cfb634bc7bf37af7d8f760f118018746ad8efbd519c4b789ac9c2e%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/06cfb634bc7bf37af7d8f760f118018746ad8efbd519c4b789ac9c2e@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5@%3Cdev.tomcat.apache.org%3E
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A10417
- https://www.redhat.com/archives/fedora-package-announce/2008-February/msg00315.html
- https://www.redhat.com/archives/fedora-package-announce/2008-February/msg00460.html
- http://lists.apple.com/archives/security-announce/2008/Oct/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2009-02/msg00002.html
- http://marc.info/?l=bugtraq&m=139344343412337&w=2
- http://security.gentoo.org/glsa/glsa-200804-10.xml
- http://securityreason.com/securityalert/3485
- http://support.apple.com/kb/HT3216
