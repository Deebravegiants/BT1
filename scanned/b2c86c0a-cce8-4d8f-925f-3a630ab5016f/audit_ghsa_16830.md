# [M] h2 servers vulnerable to degradation of service with CONTINUATION Flood

## Summary
Severity: Medium
Advisory: GHSA-q6cp-qfwq-4gcv
CWE: CWE-400, CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-q6cp-qfwq-4gcv
Type: github-advisory

## Affected
- crates.io: `h2` — affected >=0 <0.3.26
- crates.io: `h2` — affected >=0.4.0 <0.4.4

## Details
An attacker can send a flood of CONTINUATION frames, causing `h2` to process them indefinitely. This results in an increase in CPU usage.

Tokio task budget helps prevent this from a complete denial-of-service, as the server can still respond to legitimate requests, albeit with increased latency.

More details at https://seanmonstar.com/blog/hyper-http2-continuation-flood/.

Patches available for 0.4.x and 0.3.x versions.

## References
- https://github.com/hyperium/h2
- https://rustsec.org/advisories/RUSTSEC-2024-0332.html
- https://seanmonstar.com/blog/hyper-http2-continuation-flood
- https://www.kb.cert.org/vuls/id/421644
