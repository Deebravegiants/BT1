# [M] Apache Tomcat does not properly handle an invalid Transfer-Encoding header

## Summary
Severity: Medium
Advisory: GHSA-cxg2-49rq-8gcr
CVE: CVE-2010-2227
CWE: CWE-119
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cxg2-49rq-8gcr
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.2
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0 <5.5.30
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.28

## Details
Apache Tomcat 5.5.0 through 5.5.29, 6.0.0 through 6.0.27, and 7.0.0 beta does not properly handle an invalid Transfer-Encoding header, which allows remote attackers to cause a denial of service (application outage) or obtain sensitive information via a crafted header that interferes with "recycling of a buffer."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-2227
- https://github.com/apache/tomcat/commit/40e5880dfc51517334acda5f12beacdec52ca283
- https://github.com/apache/tomcat55/commit/4faaca9353e5e3f963c7a674b3ac6a0bd1c3757e
- https://web.archive.org/web/20161107200417/http://securitytracker.com/id?1024180
- https://web.archive.org/web/20140723000733/http://secunia.com/advisories/57126
- https://web.archive.org/web/20111119150528/http://www.securityfocus.com/archive/1/516397/100/0/threaded
- https://web.archive.org/web/20110906004746/http://www.securityfocus.com/bid/41544
- https://web.archive.org/web/20110716102842/http://www.securityfocus.com/archive/1/512272/100/0/threaded
- https://web.archive.org/web/20110713184518/http://secunia.com/advisories/44183
- https://web.archive.org/web/20110712000328/http://secunia.com/advisories/42368
- https://web.archive.org/web/20110220104430/http://secunia.com/advisories/42454
- https://web.archive.org/web/20110220104426/http://secunia.com/advisories/41025
- https://web.archive.org/web/20110220104410/http://secunia.com/advisories/40813
- https://web.archive.org/web/20110220095703/http://secunia.com/advisories/42079
- https://web.archive.org/web/20110213053623/http://secunia.com/advisories/43310
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A18532
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/06cfb634bc7bf37af7d8f760f118018746ad8efbd519c4b789ac9c2e@%3Cdev.tomcat.apache.org%3E
