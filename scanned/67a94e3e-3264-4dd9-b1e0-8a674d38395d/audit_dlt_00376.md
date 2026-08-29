# [?] [security] Upgrade rustls 0.21.10 to 0.21.12 to fix complete_io infinite loop DoS (#18815)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-02-23
Source: https://github.com/aptos-labs/aptos-core/commit/2cd764e7e0f366d0a1c22b9d0ceaa83683248e90
Type: security-commit

## Details
[security] Upgrade rustls 0.21.10 to 0.21.12 to fix complete_io infinite loop DoS (#18815)

Addresses CVE-2024-32650: rustls::ConnectionCommon::complete_io could fall
into an infinite loop when a client sends close_notify immediately after
client_hello. This causes 100% CPU usage on the affected thread, enabling
a denial-of-service attack against blocking rustls servers.

The fix upgrades rustls from 0.21.10 to 0.21.12 which contains the patch
for this vulnerability. This affects the following transitive dependencies:
- hyper-rustls 0.24.2
- reqwest (0.11.x)
- tokio-rustls 0.24.1
- tokio-tungstenite
- tungstenite

Note: rustls 0.20.9 (used by kube 0.65.0) remains unpatched as the 0.20.x
line is EOL with no security fix available. However, kube uses rustls via
tokio-rustls which does not call complete_io, so the vulnerable code path
is not reachable. rustls 0.22.4 and 0.23.7 are already patched.

Co-authored-by: Cursor Agent <cursoragent@cursor.com>
