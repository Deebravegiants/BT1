# [H] Apache Tomcat Allows Remote Attackers to Spoof AJP Requests

## Summary
Severity: High
Advisory: GHSA-c38m-v4m2-524v
CVE: CVE-2011-3190
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-c38m-v4m2-524v
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.21
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.34
- Maven: `org.apache.tomcat:tomcat` — affected >=5.0.0 <5.5.34

## Details
Certain AJP protocol connector implementations in Apache Tomcat 7.0.0 through 7.0.20, 6.0.0 through 6.0.33, 5.5.0 through 5.5.33, and possibly other versions allow remote attackers to spoof AJP requests, bypass authentication, and obtain sensitive information by causing the connector to interpret a request body as a new request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-3190
- https://github.com/apache/tomcat/commit/a2538ce78f83b7376c48d12d8247600079d789b1
- https://github.com/apache/tomcat55/commit/be3eb28f82250a5c81a1c42216570ebf892aefac
- https://exchange.xforce.ibmcloud.com/vulnerabilities/69472
- https://github.com/apache/tomcat
- https://issues.apache.org/bugzilla/show_bug.cgi?id=51698
- https://lists.apache.org/thread.html/06cfb634bc7bf37af7d8f760f118018746ad8efbd519c4b789ac9c2e@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5@%3Cdev.tomcat.apache.org%3E
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A14933
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A19465
- https://web.archive.org/web/20130121232525/http://www.securityfocus.com/archive/1/519466/100/0/threaded
- https://web.archive.org/web/20130314002148/http://www.securityfocus.com/bid/49353
- https://web.archive.org/web/20131214094052/http://www.securitytracker.com/id?1025993
- http://marc.info/?l=bugtraq&m=132215163318824&w=2
- http://marc.info/?l=bugtraq&m=133469267822771&w=2
- http://marc.info/?l=bugtraq&m=136485229118404&w=2
- http://marc.info/?l=bugtraq&m=139344343412337&w=2
- http://securityreason.com/securityalert/8362
