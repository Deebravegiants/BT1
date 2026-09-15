# [H] High severity vulnerability that affects com.typesafe.akka:akka-http-core_2.11 and com.typesafe.akka:akka-http-core_2.12

## Summary
Severity: High
Advisory: GHSA-9qgc-p27w-3hjg
CVE: CVE-2018-16131
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-22
Source: https://github.com/advisories/GHSA-9qgc-p27w-3hjg
Type: github-advisory

## Affected
- Maven: `com.typesafe.akka:akka-http-core_2.12` — affected >=10.1.0 <10.1.4
- Maven: `com.typesafe.akka:akka-http-core_2.11` — affected >=10.1.0 <10.1.4

## Details
The decodeRequest and decodeRequestWith directives in Lightbend Akka HTTP 10.1.x through 10.1.4 and 10.0.x through 10.0.13 allow remote attackers to cause a denial of service (memory consumption and daemon crash) via a ZIP bomb.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16131
- https://github.com/akka/akka-http/issues/2137
- https://akka.io/blog/news/2018/08/30/akka-http-dos-vulnerability-found
- https://doc.akka.io/docs/akka-http/current/security/2018-09-05-denial-of-service-via-decodeRequest.html
- https://github.com/advisories/GHSA-9qgc-p27w-3hjg
- https://groups.google.com/forum/#!topic/akka-security/Dj7INsYWdjg
