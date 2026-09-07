# [M] SwiftNIO vulnerable to Improper Neutralization of CRLF Sequences in HTTP Headers ('HTTP Response Splitting')

## Summary
Severity: Medium
Advisory: GHSA-7fj7-39wj-c64f
CVE: CVE-2022-3215
CWE: CWE-113, CWE-74
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-06-07
Source: https://github.com/advisories/GHSA-7fj7-39wj-c64f
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio` — affected >=2.41.0 <2.42.0
- SwiftURL: `github.com/apple/swift-nio` — affected >=2.39.0 <2.39.1
- SwiftURL: `github.com/apple/swift-nio` — affected >=0 <2.29.1

## Details
`NIOHTTP1` and projects using it for generating HTTP responses, including SwiftNIO, can be subject to a HTTP Response Injection attack. This occurs when a HTTP/1.1 server accepts user generated input from an incoming request and reflects it into a HTTP/1.1 response header in some form. A malicious user can add newlines to their input (usually in encoded form) and "inject" those newlines into the returned HTTP response.

This capability allows users to work around security headers and HTTP/1.1 framing headers by injecting entirely false responses or other new headers. The injected false responses may also be treated as the response to subsequent requests, which can lead to XSS, cache poisoning, and a number of other flaws.

This issue was resolved by adding a default channel handler that polices outbound headers. This channel handler is added by default to channel pipelines, but can be removed by users if they are doing this validation themselves.

## References
- https://github.com/apple/swift-nio/security/advisories/GHSA-7fj7-39wj-c64f
- https://nvd.nist.gov/vuln/detail/CVE-2022-3215
- https://github.com/apple/swift-nio/commit/a16e2f54a25b2af217044e5168997009a505930f
- https://github.com/apple/swift-nio
