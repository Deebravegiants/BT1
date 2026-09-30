# [H] Apache Tomcat allows remote attackers to read JSP source files

## Summary
Severity: High
Advisory: GHSA-qrcx-p4rr-g48h
CVE: CVE-2005-4836
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-qrcx-p4rr-g48h
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=4.1.15

## Details
The HTTP/1.1 connector in Apache Tomcat 4.1.15 through 4.1.40 does not reject NULL bytes in a URL when allowLinking is configured, which allows remote attackers to read JSP source files and obtain sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2005-4836
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3@%3Cdev.tomcat.apache.org%3E
- http://tomcat.apache.org/security-4.html
- http://www.securityfocus.com/bid/28483
