# [M] Netty denial of service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7vpq-g998-qpv7
CVE: CVE-2014-0193
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7vpq-g998-qpv7
Type: github-advisory

## Affected
- Maven: `io.netty:netty` — affected >=3.6.0.Beta1 <3.6.9.Final
- Maven: `io.netty:netty` — affected >=3.7.0.Final <3.7.1.Final
- Maven: `io.netty:netty` — affected >=3.8.0.Final <3.8.2.Final
- Maven: `io.netty:netty` — affected >=3.9.0.Final <3.9.1.Final
- Maven: `io.netty:netty` — affected >=4.0.0.Alpha1 <4.0.19.Final
- Maven: `io.netty:netty-all` — affected >=4.0.0.Alpha1 <4.0.19.Final

## Details
`WebSocket08FrameDecoder` in Netty 3.6.x before 3.6.9, 3.7.x before 3.7.1, 3.8.x before 3.8.2, 3.9.x before 3.9.1, and 4.0.x before 4.0.19 allows remote attackers to cause a denial of service (memory consumption) via a `TextWebSocketFrame` followed by a long stream of `ContinuationWebSocketFrames`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0193
- https://github.com/netty/netty/issues/2441
- https://github.com/netty/netty/commit/8599ab5bdb761bb99d41a975d689f74c12e4892b
- https://github.com/netty/netty
- https://lists.apache.org/thread.html/ff8dcfe29377088ab655fda9d585dccd5b1f07fabd94ae84fd60a7f8%40%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/ff8dcfe29377088ab655fda9d585dccd5b1f07fabd94ae84fd60a7f8@%3Ccommits.pulsar.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/02/msg00018.html
- https://web.archive.org/web/20140509033427/http://www.securityfocus.com/bid/67182
- https://web.archive.org/web/20140509044857/http://secunia.com/advisories/58280
- https://web.archive.org/web/20161119201425/http://secunia.com/advisories/59290
- http://netty.io/news/2014/04/30/release-day.html
- http://rhn.redhat.com/errata/RHSA-2014-1019.html
- http://rhn.redhat.com/errata/RHSA-2014-1020.html
- http://rhn.redhat.com/errata/RHSA-2014-1021.html
- http://rhn.redhat.com/errata/RHSA-2014-1351.html
- http://rhn.redhat.com/errata/RHSA-2015-0675.html
- http://rhn.redhat.com/errata/RHSA-2015-0720.html
- http://rhn.redhat.com/errata/RHSA-2015-0765.html
