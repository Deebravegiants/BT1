# [M] Apache Tomcat Leaks Information via Error Message

## Summary
Severity: Medium
Advisory: GHSA-m8w6-7rh6-4xj6
CVE: CVE-2002-2008
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-m8w6-7rh6-4xj6
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <4.1.3

## Details
Apache Tomcat 4.0.3 for Windows allows remote attackers to obtain the web root path via an HTTP request for a resource that does not exist, such as lpt9, which leaks the information in an error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2002-2008
- https://github.com/apache/tomcat
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3@%3Cdev.tomcat.apache.org%3E
- https://web.archive.org/web/20200815000000*/http://www.securityfocus.com/bid/5054
- http://archives.neohapsis.com/archives/bugtraq/2002-06/0225.html
- http://tomcat.apache.org/security-4.html
- http://www.iss.net/security_center/static/9394.php
