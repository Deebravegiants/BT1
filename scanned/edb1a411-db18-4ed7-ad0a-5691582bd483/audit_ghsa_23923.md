# [M] Apache Tomcat does not follow ServletSecurity annotations

## Summary
Severity: Medium
Advisory: GHSA-vch7-92vf-jm44
CVE: CVE-2011-1419
CWE: CWE-284
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vch7-92vf-jm44
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0 <7.0.11

## Details
Apache Tomcat 7.x before 7.0.11, when web.xml has no security constraints, does not follow ServletSecurity annotations, which allows remote attackers to bypass intended access restrictions via HTTP requests to a web application.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2011-1088.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1419
- https://github.com/apache/tomcat/commit/0ff4905158b77787a7f3aca55c9dec93456665dc
- https://github.com/apache/tomcat/commit/3e5b0455483eed55752047073e92403bfca8d3ec
- https://exchange.xforce.ibmcloud.com/vulnerabilities/65971
- https://exchange.xforce.ibmcloud.com/vulnerabilities/66154
- https://github.com/apache/tomcat
- https://web.archive.org/web/20110307182442/http://markmail.org/message/yzmyn44f5aetmm2r
- https://web.archive.org/web/20110323002552/http://markmail.org/message/lzx5273wsgl5pob6
- https://web.archive.org/web/20170202135440/http://www.securityfocus.com/bid/46685
- http://mail-archives.apache.org/mod_mbox/www-announce/201103.mbox/%3C4D6E74FF.7050106@apache.org%3E
- http://marc.info/?l=tomcat-user&m=129966773405409&w=2
- http://svn.apache.org/viewvc?view=revision&revision=1079752
- http://tomcat.apache.org/security-7.html
