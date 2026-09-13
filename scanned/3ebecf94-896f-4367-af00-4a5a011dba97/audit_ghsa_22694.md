# [H] Apache Tomcat Vulnerable to Denial of Service (DoS) via Simultaneous Requests

## Summary
Severity: High
Advisory: GHSA-8f4w-jwqv-5cxc
CVE: CVE-2005-3510
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-8f4w-jwqv-5cxc
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0 <5.5.12

## Details
Apache Tomcat 5.5.0 to 5.5.11 allows remote attackers to cause a denial of service (CPU consumption) via a large number of simultaneous requests to list a web directory that has a large number of files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2005-3510
- https://github.com/apache/tomcat
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3@%3Cdev.tomcat.apache.org%3E
- https://web.archive.org/web/20200228054210/http://www.securityfocus.com/archive/1/415782/30/0/threaded
- https://web.archive.org/web/20200229175931/http://www.securityfocus.com/bid/15325
- https://web.archive.org/web/20200517122628/http://www.securityfocus.com/archive/1/500396/100/0/threaded
- https://web.archive.org/web/20200517153851/http://www.securityfocus.com/archive/1/500412/100/0/threaded
- https://web.archive.org/web/20200922015809/http://securitytracker.com/id?1015147
- http://community.ca.com/blogs/casecurityresponseblog/archive/2009/01/23.aspx
- http://sunsolve.sun.com/search/document.do?assetkey=1-26-239312-1
- http://support.ca.com/irj/portal/anonymous/phpsupcontent?contentID=197540
- http://tomcat.apache.org/security-4.html
- http://tomcat.apache.org/security-5.html
- http://www.redhat.com/support/errata/RHSA-2006-0161.html
- http://www.redhat.com/support/errata/RHSA-2008-0261.html
