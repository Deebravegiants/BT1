# [M] Apache Tomcat Source Code Disclosure

## Summary
Severity: Medium
Advisory: GHSA-jxcv-v856-j5vg
CVE: CVE-2002-1148
CWE: CWE-200
Ecosystem: Maven
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-jxcv-v856-j5vg
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=4.0.0 <4.0.5
- Maven: `org.apache.tomcat:tomcat` — affected >=4.1.0 <4.1.12

## Details
The default servlet (`org.apache.catalina.servlets.DefaultServlet`) in Tomcat 4.0.4 and 4.1.10 and earlier allows remote attackers to read source code for server files via a direct request to the servlet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2002-1148
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5@<dev.tomcat.apache.org>
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74@<dev.tomcat.apache.org>
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3@<dev.tomcat.apache.org>
- https://web.archive.org/web/20021027204137/http://www.iss.net/security_center/static/10175.php
- https://web.archive.org/web/20030113141130/http://online.securityfocus.com/advisories/4758
- https://web.archive.org/web/20030710185447/http://www.securityfocus.com/bid/5786
- https://web.archive.org/web/20040814165854/http://rhn.redhat.com/errata/RHSA-2002-217.html
- https://web.archive.org/web/20040817035804/http://rhn.redhat.com/errata/RHSA-2002-218.html
- https://web.archive.org/web/20070430075037/http://www.debian.org/security/2002/dsa-170
- http://marc.info/?l=bugtraq&m=103288242014253&w=2
