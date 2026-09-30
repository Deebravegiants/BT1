# [M] CVE-2026-43678

## Summary
Severity: Medium
Advisory: CVE-2026-43678
Aliases: GHSA-qcc5-f287-vgmq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-43678
Type: osv

## Details
An unauthenticated remote peer can crash any NIOWebSocket-based server (including Vapor and Hummingbird) with a single 11-byte frame sent after a completed WebSocket handshake, dropping all active connections until the process restarts. This vulnerability is addressed in swift-nio version 2.101.0.

## References
- https://github.com/apple/swift-nio/security/advisories/GHSA-qcc5-f287-vgmq
