# [M] Apache Tomcat Cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f98p-9pp6-7q6c
CVE: CVE-2008-1947
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-f98p-9pp6-7q6c
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.9 <5.5.27
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.18
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=5.5.9 <5.5.27
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=6.0.0 <6.0.18

## Details
Cross-site scripting (XSS) vulnerability in Apache Tomcat 5.5.9 through 5.5.26 and 6.0.0 through 6.0.16 allows remote attackers to inject arbitrary web script or HTML via the name parameter (aka the hostname attribute) to `host-manager/html/add`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-1947
- https://github.com/apache/tomcat/commit/ab6a6c41ac972c845717c9d639f0335865afab4d
- https://github.com/apache/tomcat/commit/78ad0fcbe29c824f1f2e45a4e2716247b033250a
- https://github.com/apache/tomcat/commit/49c71fc59c1b8f8da77aea9eb53e61db168aebab
- https://github.com/apache/tomcat/commit/5f00d434c8dc11bd49ce0b4b56fe889839056030
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5@%3Cdev.tomcat.apache.org%3E
- https://lists.apple.com/archives/security-announce/2008/Oct/msg00001.html
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A11534
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A6009
- https://web.archive.org/web/20200514224656/http://www.securityfocus.com/archive/1/507985/100/0/threaded
- https://web.archive.org/web/20201208011750/http://www.securityfocus.com/archive/1/492958/100/0/threaded
- https://www.redhat.com/archives/fedora-package-announce/2008-September/msg00712.html
- https://www.redhat.com/archives/fedora-package-announce/2008-September/msg00859.html
- https://www.redhat.com/archives/fedora-package-announce/2008-September/msg00889.html
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/06cfb634bc7bf37af7d8f760f118018746ad8efbd519c4b789ac9c2e@%3Cdev.tomcat.apache.org%3E
