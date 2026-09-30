# [H] SwiftNIO Extras vulnerable to improper detection of complete HTTP body decompression

## Summary
Severity: High
Advisory: GHSA-773g-x274-8qmf
CVE: CVE-2022-3252
CWE: CWE-835
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-07
Source: https://github.com/advisories/GHSA-773g-x274-8qmf
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio-extras` — affected >=1.11.0 <1.14.0
- SwiftURL: `github.com/apple/swift-nio-extras` — affected >=1.10.0 <1.10.3
- SwiftURL: `github.com/apple/swift-nio-extras` — affected >=0 <1.9.2

## Details
SwiftNIO Extras provides a pair of helpers for transparently decompressing received HTTP request or response bodies. These two objects (`HTTPRequestDecompressor` and `HTTPResponseDecompressor`) both failed to detect when the decompressed body was considered complete. If trailing junk data was appended to the HTTP message body, the code would repeatedly attempt to decompress this data and fail. This would lead to an infinite loop making no forward progress, leading to livelock of the system and denial-of-service.

This issue can be triggered by any attacker capable of sending a compressed HTTP message. Most commonly this is HTTP servers, as compressed HTTP messages cannot be negotiated for HTTP requests, but it is possible that users have configured decompression for HTTP requests as well. The attack is low effort, and likely to be reached without requiring any privilege or system access. The impact on availability is high: the process immediately becomes unavailable but does not immediately crash, meaning that it is possible for the process to remain in this state until an administrator intervenes or an automated circuit breaker fires. If left unchecked this issue will very slowly exhaust memory resources due to repeated buffer allocation, but the buffers are not written to and so it is possible that the processes will not terminate for quite some time.

This risk can be mitigated by removing transparent HTTP message decompression. The issue is fixed by correctly detecting the termination of the compressed body as reported by zlib and refusing to decompress further data.

## References
- https://github.com/apple/swift-nio-extras/security/advisories/GHSA-773g-x274-8qmf
- https://nvd.nist.gov/vuln/detail/CVE-2022-3252
- https://github.com/apple/swift-nio-extras/pull/177
- https://github.com/apple/swift-nio-extras/pull/177/commits/359015de2c49e426c27b1d25dbf599b08a9d3ee6
- https://github.com/apple/swift-nio-extras
