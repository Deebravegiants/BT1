# [M] Apache Tomcat HTTP BIO Connector Error Discloses Information From Different Requests to Remote Users

## Summary
Severity: Medium
Advisory: GHSA-h6c8-rg87-f3pc
CVE: CVE-2011-1475
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-h6c8-rg87-f3pc
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.12

## Details
The HTTP BIO connector in Apache Tomcat 7.0.x before 7.0.12 does not properly handle HTTP pipelining, which allows remote attackers to read responses intended for other clients in opportunistic circumstances by examining the application data in HTTP packets, related to "a mix-up of responses for requests from different users."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1475
- https://github.com/apache/tomcat/commit/d2e8f2ede7dea39f75f68384f331f38f094e4ed3
- https://github.com/apache/tomcat/commit/fd8a579e0e2379a84826b11700adf396e4ed2041
- https://exchange.xforce.ibmcloud.com/vulnerabilities/66676
- https://github.com/apache/tomcat
- https://issues.apache.org/bugzilla/show_bug.cgi?id=50957
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A12374
- https://web.archive.org/web/20120605200856/http://www.securityfocus.com/bid/47199
- https://web.archive.org/web/20170202012852/http://www.securityfocus.com/archive/1/517363
- https://web.archive.org/web/20170317142459/http://www.securitytracker.com/id?1025303
- http://seclists.org/fulldisclosure/2011/Apr/97
- http://svn.apache.org/viewvc?view=revision&revision=1086349
- http://svn.apache.org/viewvc?view=revision&revision=1086352
- http://tomcat.apache.org/security-7.html
