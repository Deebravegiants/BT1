# [M] Improper Neutralization of Input During Web Page Generation in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-3p86-xgrq-m6p6
CVE: CVE-2011-0013
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-3p86-xgrq-m6p6
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0 <5.5.32
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.30
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.6

## Details
Multiple cross-site scripting (XSS) vulnerabilities in the HTML Manager Interface in Apache Tomcat 5.5 before 5.5.32, 6.0 before 6.0.30, and 7.0 before 7.0.6 allow remote attackers to inject arbitrary web script or HTML, as demonstrated via the display-name tag.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-0013
- https://github.com/apache/tomcat/commit/58223c5ecc0751c3642c810f291b8f033d33b97f
- https://github.com/apache/tomcat55/commit/863d77c7d321245de019ac32252828e0a025c5b4
- https://web.archive.org/web/20151017023138/http://secunia.com/advisories/57126
- https://web.archive.org/web/20120213130147/http://www.securityfocus.com/bid/46174
- https://web.archive.org/web/20120126070320/http://www.securitytracker.com/id?1025026
- https://web.archive.org/web/20120126065143/http://www.securityfocus.com/archive/1/516209/30/90/threaded
- https://web.archive.org/web/20111229163935/http://secunia.com/advisories/43192
- https://web.archive.org/web/20111227000129/http://secunia.com/advisories/45022
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A19269
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A14945
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A12878
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/06cfb634bc7bf37af7d8f760f118018746ad8efbd519c4b789ac9c2e@%3Cdev.tomcat.apache.org%3E
- https://github.com/apache/tomcat
- https://bugzilla.redhat.com/show_bug.cgi?id=675786
- https://access.redhat.com/security/cve/CVE-2011-0013
- https://access.redhat.com/errata/RHSA-2011:1845
