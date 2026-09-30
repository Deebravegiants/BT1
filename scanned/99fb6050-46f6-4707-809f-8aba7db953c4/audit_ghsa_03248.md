# [M] HTTP Request Smuggling in akka-http-core

## Summary
Severity: Medium
Advisory: GHSA-2w7w-2j92-44hx
CVE: CVE-2021-23339
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-2w7w-2j92-44hx
Type: github-advisory

## Affected
- Maven: `com.typesafe.akka:akka-http-core` — affected >=10.2.0 <10.2.4
- Maven: `com.typesafe.akka:akka-http-core` — affected >=0 <10.1.14

## Details
A vulnerable Akka HTTP server will accept a malformed message and hand it over to the user. If the user application proxies this message to another server unchanged and that server also accepts that message but interprets it as two HTTP messages, the second message has reached the second server without having been inspected by the proxy.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23339
- https://github.com/akka/akka-http/pull/3754%23issuecomment-779265201
- https://github.com/akka/akka-http/commit/e3a4935151c91cee28e65e6b894dd50839ef9d34
- https://doc.akka.io/docs/akka-http/10.1/security/2021-02-24-incorrect-handling-of-Transfer-Encoding-header.html
- https://snyk.io/vuln/SNYK-JAVA-COMTYPESAFEAKKA-1075043
