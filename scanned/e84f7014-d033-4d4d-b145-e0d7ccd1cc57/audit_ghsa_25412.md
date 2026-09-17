# [H] Apache Traffic Control vulnerable to Slowloris-style Denial of Service attack

## Summary
Severity: High
Advisory: GHSA-f2wr-c4c4-xjg7
CVE: CVE-2017-7670
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-f2wr-c4c4-xjg7
Type: github-advisory

## Affected
- Go: `github.com/apache/trafficcontrol` — affected >=1.1.4 <1.8.1
- Go: `github.com/apache/trafficcontrol` — affected >=2.0.0-RC0 <2.0.0
- Go: `github.com/apache/trafficcontrol` — affected >=2.1.0-RC0 <2.1.0-RC1
- Go: `github.com/apache/trafficcontrol` — affected >=0 <0.0.0-20170531185407-738c10fa1b58
- Go: `github.com/apache/trafficcontrol` — affected >=0.0.0 <1.1.4-0.20170531185407-738c10fa1b58

## Details
The Traffic Router component of the incubating Apache Traffic Control project is vulnerable to a Slowloris style Denial of Service attack. TCP connections made on the configured DNS port will remain in the `ESTABLISHED` state until the client explicitly closes the connection or Traffic Router is restarted. If connections remain in the `ESTABLISHED` state indefinitely and accumulate in number to match the size of the thread pool dedicated to processing DNS requests, the thread pool becomes exhausted. Once the thread pool is exhausted, Traffic Router is unable to service any DNS request, regardless of transport protocol.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7670
- https://github.com/apache/trafficcontrol/pull/633
- https://github.com/apache/trafficcontrol/pull/634
- https://github.com/apache/trafficcontrol/commit/738c10fa1b5861e4cc3944dc7c3065d16f4a708c
- https://github.com/apache/trafficcontrol
- https://lists.apache.org/thread.html/42b207e9f526353b504591684bd02a5e9fcb4b8f28534253d07740a0@%3Cusers.trafficcontrol.apache.org%3E
- https://lists.apache.org/thread.html/bb09fc29e9c2ee85b118a3d5748a8a523d30cf691ff8b606c6a1748c@%3Ccommits.trafficcontrol.apache.org%3E
- https://lists.apache.org/thread.html/r3c675031ac220b5eae64a9c84a03ee60045c6045738607dca4a96cb8@%3Ccommits.trafficcontrol.apache.org%3E
