# [M] Denial of service in Netty

## Summary
Severity: Medium
Advisory: GHSA-9959-6p3m-wxpc
CVE: CVE-2014-3488
CWE: CWE-119
Ecosystem: Maven
Published: 2020-06-30
Source: https://github.com/advisories/GHSA-9959-6p3m-wxpc
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler` — affected >=0 <3.9.2

## Details
The SslHandler in Netty before 3.9.2 allows remote attackers to cause a denial of service (infinite loop and CPU consumption) via a crafted SSLv2Hello message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3488
- https://github.com/netty/netty/issues/2562
- https://github.com/netty/netty/commit/2fa9400a59d0563a66908aba55c41e7285a04994
- https://github.com/netty/netty
- https://lists.debian.org/debian-lts-announce/2020/02/msg00018.html
- https://snyk.io/vuln/SNYK-JAVA-ORGJBOSSNETTY-31630
- http://netty.io/news/2014/06/11/3-9-2-Final.html
- http://secunia.com/advisories/59196
