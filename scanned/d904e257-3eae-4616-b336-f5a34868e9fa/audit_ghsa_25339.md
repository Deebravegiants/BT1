# [M] Access restriction bypass in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-3xpj-jgv5-q4vv
CVE: CVE-2011-1582
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3xpj-jgv5-q4vv
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.12 <7.0.14

## Details
Apache Tomcat 7.0.12 and 7.0.13 processes the first request to a servlet without following security constraints that have been configured through annotations, which allows remote attackers to bypass intended access restrictions via HTTP requests.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2011-1088, CVE-2011-1183, and CVE-2011-1419.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1582
- https://github.com/apache/tomcat/commit/299b26af66793438c323ea6b18462fa44683080f
- https://exchange.xforce.ibmcloud.com/vulnerabilities/67515
- https://github.com/apache/tomcat
- https://web.archive.org/web/20111110135226/http://www.securityfocus.com/archive/1/518032/100/0/threaded
- https://web.archive.org/web/20170202135510/http://www.securityfocus.com/bid/47886
- http://mail-archives.apache.org/mod_mbox/www-announce/201105.mbox/%3C4DD26E30.2060103@apache.org%3E
- http://securityreason.com/securityalert/8256
- http://svn.apache.org/viewvc?view=revision&revision=1100832
- http://tomcat.apache.org/security-7.html#Fixed_in_Apache_Tomcat_7.0.14_%28released_12_May_2011%29
