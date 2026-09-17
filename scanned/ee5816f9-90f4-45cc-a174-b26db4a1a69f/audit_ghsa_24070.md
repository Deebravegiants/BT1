# [M] Apache Tomcat Allows Replacing of XML Parser

## Summary
Severity: Medium
Advisory: GHSA-r7c8-hghc-2mp8
CVE: CVE-2011-2481
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-r7c8-hghc-2mp8
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.17

## Details
Apache Tomcat 7.0.x before 7.0.17 permits web applications to replace an XML parser used for other web applications, which allows local users to read or modify the (1) web.xml, (2) context.xml, or (3) tld files of arbitrary web applications via a crafted application that is loaded earlier than the target application.  NOTE: this vulnerability exists because of a CVE-2009-0783 regression.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2481
- https://github.com/apache/tomcat/commit/279e4451cb996f810fbca2f78b6340412d9daa7b
- https://github.com/apache/tomcat
- https://issues.apache.org/bugzilla/show_bug.cgi?id=51395
- https://web.archive.org/web/20111209022500/http://www.securityfocus.com/bid/49147
- https://web.archive.org/web/20161127215021/http://securitytracker.com/id?1025924
- http://marc.info/?l=bugtraq&m=139344343412337&w=2
- http://svn.apache.org/viewvc?view=revision&revision=1137753
- http://svn.apache.org/viewvc?view=revision&revision=1138788
- http://tomcat.apache.org/security-7.html
