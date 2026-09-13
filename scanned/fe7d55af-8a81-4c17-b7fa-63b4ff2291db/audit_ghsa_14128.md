# [C] SwiftNIO vulnerable to HTTP request smuggling using malformed Transfer-Encoding header

## Summary
Severity: Critical
Advisory: GHSA-mgc4-wqv7-4pxm
CWE: CWE-444
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-18
Source: https://github.com/advisories/GHSA-mgc4-wqv7-4pxm
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio` — affected >=1.0.0 <1.14.2
- SwiftURL: `github.com/apple/swift-nio` — affected >=2.0.0 <2.13.1

## Details
### Impact

Affected SwiftNIO systems are vulnerable to request smuggling attacks, in which they parse a given HTTP message differently from other network parties, potentially seeing a different number of requests than other servers. This can lead to failures of authentication, routing, and other issues.

This vulnerability can be found in the bundled copy of the Node.JS HTTP parser used in the `NIOHTTP1` module.

### Workarounds

No workaround is available, users must upgrade.

### References

https://nodejs.org/en/blog/vulnerability/february-2020-security-releases/#http-request-smuggling-using-malformed-transfer-encoding-header-critical-cve-2019-15605

## References
- https://github.com/apple/swift-nio/security/advisories/GHSA-mgc4-wqv7-4pxm
- https://github.com/apple/swift-nio/pull/1387
- https://github.com/apple/swift-nio/pull/1388
- https://github.com/apple/swift-nio/commit/8da5c5a4e6c5084c296b9f39dc54f00be146e0fa
- https://github.com/apple/swift-nio/commit/bfde40cac8eca25ce021552513b20ee23fc6e306
- https://github.com/apple/swift-nio/commit/df9390006bce7da1b6273f804d3acbbfdfcc6154
- https://github.com/apple/swift-nio/commit/f94b22b506e3557cb1b325534fa9bbcd39c90246
- https://github.com/apple/swift-nio
