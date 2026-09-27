# [M] Access controll bypass in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-p26v-97vp-jcx6
CVE: CVE-2011-1183
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-p26v-97vp-jcx6
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.11 <7.0.12

## Details
Apache Tomcat 7.0.11, when web.xml has no login configuration, does not follow security constraints, which allows remote attackers to bypass intended access restrictions via HTTP requests to a meta-data complete web application.  NOTE: this vulnerability exists because of an incorrect fix for CVE-2011-1088 and CVE-2011-1419.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1183
- https://github.com/apache/tomcat/commit/b7b5c63a932f6c1ea05f9b65ad9054247bb5af57
- https://exchange.xforce.ibmcloud.com/vulnerabilities/66675
- https://github.com/apache/tomcat
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A12701
- https://web.archive.org/web/20200229122300/http://www.securityfocus.com/bid/47196
- https://web.archive.org/web/20200928033804/http://www.securityfocus.com/archive/1/517362/100/0/threaded
- http://seclists.org/fulldisclosure/2011/Apr/96
- http://securityreason.com/securityalert/8187
- http://svn.apache.org/viewvc?view=revision&revision=1087643
- http://tomcat.apache.org/security-7.html
