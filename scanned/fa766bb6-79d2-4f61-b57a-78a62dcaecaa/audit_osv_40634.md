# [M] MCP Kotlin SDK's unbounded line buffer in StdioServerTransport/StdioClientTransport leads to memory exhaustion (DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-53937
Aliases: GHSA-74gp-qhv5-v493
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-53937
Type: osv

## Details
MCP Kotlin SDK is the Kotlin Multiplatform software development kit for the Model Context Protocol. In versions 0.7.0 through 0.12.0, `ReadBuffer.append` in `kotlin-sdk-core/src/commonMain/kotlin/io/modelcontextprotocol/kotlin/sdk/shared/ReadBuffer.kt` writes every chunk of bytes received from the stdio transport into a `kotlinx.io.Buffer` with no size cap. Frames are extracted from that buffer only when a `\n` (0x0a) byte is observed. A peer that streams bytes without ever sending a newline causes the internal buffer to grow indefinitely until the JVM (or the surrounding host process) is OOM-killed. The leak is amplified by `StdioServerTransport` and `StdioClientTransport`, which both queue raw chunks through a `kotlinx.coroutines.channels.Channel<ByteArray>(Channel.UNLIMITED)` and then call `readBuffer.append(chunk)` without backpressure or size guard. This is a remote-pre-auth denial of service whenever an SDK stdio server's stdin is fed by an untrusted or attacker-controlled producer (for example: a host program that exec's the MCP server as a subprocess and pipes through bytes received from a network peer, or a sidecar wrapper that proxies bytes from an HTTP endpoint to the stdio transport). Version 0.13.0 fixes the issue.

## References
- https://github.com/modelcontextprotocol/kotlin-sdk/blob/6d5bac1/kotlin-sdk-core/src/commonMain/kotlin/io/modelcontextprotocol/kotlin/sdk/shared/ReadBuffer.kt
- https://github.com/modelcontextprotocol/kotlin-sdk/releases/tag/0.13.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53937.json
- https://github.com/modelcontextprotocol/kotlin-sdk/security/advisories/GHSA-74gp-qhv5-v493
- https://nvd.nist.gov/vuln/detail/CVE-2026-53937
- https://github.com/modelcontextprotocol/kotlin-sdk/commit/6e6f80512fb8fcc9f3c031cfd693ccbcf9c4aaab
