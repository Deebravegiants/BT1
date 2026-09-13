# [M] rpcx - Denial of Service via Gzip Decompression Bomb in Wire Protocol

## Summary
Severity: Medium
Advisory: CVE-2026-59803
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59803
Type: osv

## Details
rpcx through 1.9.3, fixed in commit 047aec1, contains a denial-of-service vulnerability in protocol.Message.Decode (protocol/message.go). When a message has the compression flag set, the payload is gzip-decompressed via util.Unzip with no limit on the decompressed output size. The only built-in size guard, protocol.MaxMessageLength, is checked against the compressed on-the-wire frame length, not the decompressed size, so it provides no protection. Because decoding (and decompression) occurs in readRequest before authentication, a single unauthenticated connection can send a small (under 2 MB) gzip-compressed message that expands to gigabytes of heap allocation, leading to out-of-memory conditions and service unavailability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59803.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59803
- https://www.vulncheck.com/advisories/rpcx-denial-of-service-via-gzip-decompression-bomb-in-wire-protocol
- https://github.com/smallnest/rpcx/pull/943
- https://github.com/smallnest/rpcx/commit/047aec18efa7d037105e2b72c36dd2ae05e1acc6
- https://github.com/smallnest/rpcx
- https://github.com/smallnest/rpcx/issues/942
