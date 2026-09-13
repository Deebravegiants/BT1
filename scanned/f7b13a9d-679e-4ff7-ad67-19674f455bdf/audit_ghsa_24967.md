# [M] Apache Tomcat treats single quotes as delimiters in cookies

## Summary
Severity: Medium
Advisory: GHSA-qff8-g48j-pwpw
CVE: CVE-2007-3382
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-qff8-g48j-pwpw
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0
- Maven: `org.apache.tomcat:tomcat` — affected >=5.0.0
- Maven: `org.apache.tomcat:tomcat` — affected >=4.1.0
- Maven: `org.apache.tomcat:tomcat` — affected >=3.3.0

## Details
Apache Tomcat 6.0.0 to 6.0.13, 5.5.0 to 5.5.24, 5.0.0 to 5.0.30, 4.1.0 to 4.1.36, and 3.3 to 3.3.2 treats single quotes (`'`) as delimiters in cookies, which might cause sensitive information such as session IDs to be leaked and allow remote attackers to conduct session hijacking attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-3382
- https://exchange.xforce.ibmcloud.com/vulnerabilities/36006
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3@%3Cdev.tomcat.apache.org%3E
- https://www.redhat.com/archives/fedora-package-announce/2007-November/msg00525.html
- http://community.ca.com/blogs/casecurityresponseblog/archive/2009/01/23.aspx
- http://lists.apple.com/archives/security-announce/2008//Jun/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2008-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2009-02/msg00002.html
- http://support.apple.com/kb/HT2163
- http://tomcat.apache.org/security-6.html
- http://www.debian.org/security/2008/dsa-1447
- http://www.debian.org/security/2008/dsa-1453
- http://www.redhat.com/support/errata/RHSA-2007-0871.html
- http://www.redhat.com/support/errata/RHSA-2007-0950.html
- http://www.redhat.com/support/errata/RHSA-2008-0195.html
- http://www.redhat.com/support/errata/RHSA-2008-0261.html
