# [?] fix: harness tests random panic (#10933)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2025-08-22
Source: https://github.com/ipfs/kubo/commit/fae08d66335f185d4016fa3f162a5aa178839253
Type: security-commit

## Details
fix: harness tests random panic (#10933)

* fix: harness tests random panic

Connecting nodes in parallel can cause TLS handshake failures. For each node, connect to the other nodes serially. It is not necessary to connect in parallel as it does not save any significant time.

Closes #10932

(cherry picked from commit ae068a806181dc09d4d679ba8d3c6e5f3547afac)
