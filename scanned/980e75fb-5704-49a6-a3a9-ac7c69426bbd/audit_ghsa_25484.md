# [H] Uncontrolled Recursion in Akka HTTP

## Summary
Severity: High
Advisory: GHSA-3hw2-h67c-wq66
CVE: CVE-2021-42697
CWE: CWE-674, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3hw2-h67c-wq66
Type: github-advisory

## Affected
- Maven: `com.typesafe.akka:akka-http-core_2.13.0-RC3` — affected >=10.1.0
- Maven: `com.typesafe.akka:akka-http-core_2.13.0-RC2` — affected >=10.1.0
- Maven: `com.typesafe.akka:akka-http-core_2.13.0-M5` — affected >=10.1.0
- Maven: `com.typesafe.akka:aakka-http-core_2.13.0-M3` — affected >=10.1.0
- Maven: `com.typesafe.akka:akka-http-core_2.13` — affected >=10.1.0 <10.1.15
- Maven: `com.typesafe.akka:akka-http-core_2.13` — affected >=10.2.0-M1 <10.2.7
- Maven: `com.typesafe.akka:akka-http-core_2.12` — affected >=10.1.0 <10.1.15
- Maven: `com.typesafe.akka:akka-http-core_2.12` — affected >=10.2.0-M1 <10.2.7
- Maven: `com.typesafe.akka:akka-http-core_2.11` — affected >=10.1.0 <10.1.15

## Details
Akka HTTP 10.1.x and 10.2.x before 10.2.7 can encounter stack exhaustion while parsing HTTP headers, which allows a remote attacker to conduct a Denial of Service attack by sending a User-Agent header with deeply nested comments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42697
- https://github.com/akka/akka-http/pull/3924
- https://akka.io/blog
- https://akka.io/blog/news/2021/11/02/akka-http-10.2.7-released
- https://akka.io/blog/news/2021/11/22/akka-http-10.1.15-released
- https://doc.akka.io/docs/akka-http/current/security/2021-CVE-2021-42697-stack-overflow-parsing-user-agent.html
- https://github.com/akka/akka-http
- http://packetstormsecurity.com/files/167018/Akka-HTTP-10.1.14-Denial-Of-Service.html
