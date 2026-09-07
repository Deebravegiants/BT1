# [M] Authentication Bypass in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-q9xf-jwr4-v445
CVE: CVE-2011-1184
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-q9xf-jwr4-v445
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0 <5.5.34
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.33
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.12

## Details
The HTTP Digest Access Authentication implementation in Apache Tomcat 5.5.x before 5.5.34, 6.x before 6.0.33, and 7.x before 7.0.12 does not have the expected countermeasures against replay attacks, which makes it easier for remote attackers to bypass intended access restrictions by sniffing the network for valid requests, related to lack of checking of nonce (aka server nonce) and nc (aka nonce-count or client nonce count) values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1184
- https://github.com/apache/tomcat/commit/639e20992a66d7a42fb59c974db91c8a0f730a1e
- https://github.com/apache/tomcat55/commit/644dfdf96cf82fcd2a2046d93f2b5495f7e94584
- https://github.com/apache/tomcat
- https://lists.apache.org/thread.html/06cfb634bc7bf37af7d8f760f118018746ad8efbd519c4b789ac9c2e@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8dcaf7c3894d66cb717646ea1504ea6e300021c85bb4e677dc16b1aa@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3aacc40356defc3f248aa504b1e48e819dd0471a0a83349080c6bcbf@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r584a714f141eff7b1c358d4679288177bd4ca4558e9999d15867d4b5@%3Cdev.tomcat.apache.org%3E
