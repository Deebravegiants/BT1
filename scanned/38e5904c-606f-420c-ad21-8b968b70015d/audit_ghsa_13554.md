# [H] quic-go vulnerable to pointer dereference that can lead to panic

## Summary
Severity: High
Advisory: GHSA-3q6m-v84f-6p9h
CVE: CVE-2023-46239
CWE: CWE-248, CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-30
Source: https://github.com/advisories/GHSA-3q6m-v84f-6p9h
Type: github-advisory

## Affected
- Go: `github.com/quic-go/quic-go` — affected >=0.37.0 <0.37.3

## Details
quic-go is an implementation of the [QUIC](https://datatracker.ietf.org/doc/html/rfc9000) transport protocol in Go. By serializing an ACK frame after the CRYTPO that allows a node to complete the handshake, a remote node could trigger a nil pointer dereference (leading to a panic) when the node attempted to drop the Handshake packet number space.

**Impact**

An attacker can bring down a quic-go node with very minimal effort. Completing the QUIC handshake only requires sending and receiving a few packets.

**Patches**

[v0.37.3](https://github.com/quic-go/quic-go/releases/tag/v0.37.3) contains a patch. Versions before v0.37.0 are not affected.

## References
- https://github.com/quic-go/quic-go/security/advisories/GHSA-3q6m-v84f-6p9h
- https://nvd.nist.gov/vuln/detail/CVE-2023-46239
- https://github.com/quic-go/quic-go/commit/b6a4725b60f1fe04e8f1ddcc3114e290fcea1617
- https://github.com/quic-go/quic-go
- https://github.com/quic-go/quic-go/releases/tag/v0.37.3
