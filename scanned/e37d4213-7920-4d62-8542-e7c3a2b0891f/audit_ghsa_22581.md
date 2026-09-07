# [M] Apache Tomcat XSS Vulnerabilities in Examples Web Application

## Summary
Severity: Medium
Advisory: GHSA-hc39-rjwp-qffq
CVE: CVE-2007-2449
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-hc39-rjwp-qffq
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=4.0.0
- Maven: `org.apache.tomcat:tomcat` — affected >=5.0.0
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0

## Details
Multiple cross-site scripting (XSS) vulnerabilities in certain JSP files in the examples web application in Apache Tomcat 4.0.0 through 4.0.6, 4.1.0 through 4.1.36, 5.0.0 through 5.0.30, 5.5.0 through 5.5.24, and 6.0.0 through 6.0.13 allow remote attackers to inject arbitrary web script or HTML via the portion of the URI after the `;` character, as demonstrated by a URI containing a `snp/snoop.jsp;` sequence.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-2449
- https://exchange.xforce.ibmcloud.com/vulnerabilities/34869
- https://lists.apache.org/thread.html/06cfb634bc7bf37af7d8f760f118018746ad8efbd519c4b789ac9c2e@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3@%3Cdev.tomcat.apache.org%3E
- https://www.redhat.com/archives/fedora-package-announce/2007-November/msg00525.html
- http://lists.apple.com/archives/security-announce/2008//Jun/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2008-03/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2009-02/msg00002.html
- http://rhn.redhat.com/errata/RHSA-2008-0630.html
- http://support.apple.com/kb/HT2163
- http://support.ca.com/irj/portal/anonymous/phpsupcontent?contentID=197540
- http://tomcat.apache.org/security-4.html
- http://tomcat.apache.org/security-5.html
- http://tomcat.apache.org/security-6.html
- http://www.redhat.com/support/errata/RHSA-2007-0569.html
- http://www.redhat.com/support/errata/RHSA-2008-0261.html
