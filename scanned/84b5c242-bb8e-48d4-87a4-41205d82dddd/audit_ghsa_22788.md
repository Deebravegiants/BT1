# [M] Apache Tomcat Denial of Service via Malformed Request Headers

## Summary
Severity: Medium
Advisory: GHSA-5cw4-ggx9-36vg
CVE: CVE-2009-0033
CWE: CWE-20, CWE-400
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-5cw4-ggx9-36vg
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=4.1.0
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0

## Details
Apache Tomcat 4.1.0 through 4.1.39, 5.5.0 through 5.5.27, and 6.0.0 through 6.0.18, when the Java AJP connector and mod_jk load balancing are used, allows remote attackers to cause a denial of service (application outage) via a crafted request with invalid headers, related to temporary blocking of connectors that have encountered errors, as demonstrated by an error involving a malformed HTTP Host header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-0033
- https://www.redhat.com/archives/fedora-package-announce/2009-November/msg01246.html
- https://www.redhat.com/archives/fedora-package-announce/2009-November/msg01216.html
- https://www.redhat.com/archives/fedora-package-announce/2009-November/msg01156.html
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A5739
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A19110
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A10231
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/06cfb634bc7bf37af7d8f760f118018746ad8efbd519c4b789ac9c2e@%3Cdev.tomcat.apache.org%3E
