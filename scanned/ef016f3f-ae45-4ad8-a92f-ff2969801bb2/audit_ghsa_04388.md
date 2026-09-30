# [M] NIOExtras: NIOHTTPRequestDecompressor ratio limit bypass via inflated Content-Length

## Summary
Severity: Medium
Advisory: GHSA-6ph5-fww6-vfwv
CVE: CVE-2026-28975
CWE: CWE-409, CWE-770
Ecosystem: SwiftURL
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-6ph5-fww6-vfwv
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio-extras` — affected >=0 <1.34.1

## Details
### Impact

When `NIOHTTPRequestDecompressor` is configured with `.ratio(N)`, the decompression limit is enforced using the `Content-Length` header value from the incoming request rather than the actual number of compressed bytes received. Since `Content-Length` is attacker-controlled, a malicious client can supply an inflated value that causes the ratio check to always pass, effectively disabling the configured decompression limit.

This allows an attacker to send a small, highly-compressed payload (a "gzip bomb") with a falsified `Content-Length` header to bypass the ratio-based protection entirely. The server will decompress the payload without limit, consuming unbounded memory and potentially causing denial of service.

For example, a gzip payload containing highly repetitive data can achieve amplification ratios of several hundred to one. Under `.ratio(10)` such a payload should be rejected, but if the attacker sets `Content-Length` to match the decompressed size, the check evaluates `decompressed > decompressed * 10` which is always false, and the payload is accepted without error.

Across repeated requests, this allows sustained memory amplification far exceeding the configured limits with no error raised.

### Relationship to CVE-2020-9840

GHSA-xhhr-p2r9-jmm7 (CVE-2020-9840) found that the `.size` limit checked compressed rather than decompressed bytes and recommended `.ratio` as a workaround. This advisory identifies a distinct flaw in the `.ratio` limit itself: it uses the attacker-supplied `Content-Length` header as the denominator rather than actual consumed compressed bytes. The two vulnerabilities are in the same decompression limit enforcement code but involve non-overlapping logic errors.

Users who followed the CVE-2020-9840 workaround by switching to `.ratio(N)` are affected by this vulnerability.

### Patches

Fixed in swift-nio-extras 1.34.1. The fix unifies the request and response decompressor implementations so that both accumulate actual compressed bytes received (`compressedLength += part.readableBytes`) rather than relying on any header-supplied value.

### Workarounds

Use `.size(N)` instead of `.ratio(N)` if a fixed upper bound on decompressed output is acceptable for the application. The `.size` limit is not affected by this vulnerability as it does not reference `Content-Length`.

### Credits

NIOExtras is grateful to @nathanielmiller23 for their reporting and assistance with the process.

## References
- https://github.com/apple/swift-nio-extras/security/advisories/GHSA-6ph5-fww6-vfwv
- https://github.com/apple/swift-nio-extras
