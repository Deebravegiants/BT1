# [H] Apache Tomcat may be started without proper security settings

## Summary
Severity: High
Advisory: GHSA-p543-jg43-9pm5
CVE: CVE-2002-0493
CWE: CWE-276
Ecosystem: Maven
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-p543-jg43-9pm5
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <4.0b7

## Details
Apache Tomcat may be started without proper security settings if errors are encountered while reading the `web.xml` file, which could allow attackers to bypass intended restrictions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2002-0493
- https://github.com/apache/tomcat
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3@%3Cdev.tomcat.apache.org%3E
- https://web.archive.org/web/20020903071650/http://www.iss.net/security_center/static/9863.php
- http://marc.info/?l=bugtraq&m=101709002410365&w=2
