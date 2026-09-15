# [M] swift-nio-http2 affected by HTTP/2 MadeYouReset vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xvr7-p2c6-j83w
CWE: CWE-405
Ecosystem: SwiftURL
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-13
Source: https://github.com/advisories/GHSA-xvr7-p2c6-j83w
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio-http2` — affected >=0 <1.38.0

## Details
The HTTP/2 [MadeYouReset vulnerability](https://galbarnahum.com/made-you-reset) has a mild effect on swift-nio-http2.

swift-nio-http2 mostly protects against MadeYouReset by using a number of existing denial-of-service prevention patterns that we added in response to the RapidReset vulnerabilities. The result is that servers are not vulnerable to naive attacks based on MadeYouReset, and the naive PoC examples do not affect swift-nio-http2.

However, in 1.38.0 we added some defense-in-depth measures as a precautionary measure that detect clients behaving "weirdly". These defense in depth measures tackle resource drain attacks where attackers interleave attack traffic with legitimate traffic to try to evade our existing DoS prevention mechanisms.

We recommend all adopters move to 1.38.0 as soon as possible to mitigate against more sophisticated attacks that may appear in the future.

We are very grateful to @galbarnahum, @AnatBB, and @YanivRL for their reporting and assistance with our process.

## References
- https://github.com/apple/swift-nio-http2/security/advisories/GHSA-xvr7-p2c6-j83w
- https://github.com/apple/swift-nio-http2
