# [H] Out-of-memory vulnerability in github.com/libp2p/go-libp2p

## Summary
Severity: High
Advisory: GO-2023-2024
Aliases: CVE-2023-40583, GHSA-gcq9-qqwx-rgj3
Package: github.com/libp2p/go-libp2p
Published: 2023-09-13
Source: https://osv.dev/vulnerability/GO-2023-2024
Type: chain-advisory

## Affected
- Go: `github.com/libp2p/go-libp2p` — affected >=0 <0.27.4

## Details
A malicious actor can store an arbitrary amount of data in the memory of a remote node by sending the node a message with a signed peer record. Signed peer records from randomly generated peers can be sent by a malicious actor. This memory does not get garbage collected and so the remote node can run out of memory (OOM).

## References
- https://github.com/libp2p/go-libp2p/security/advisories/GHSA-gcq9-qqwx-rgj3
- https://github.com/libp2p/go-libp2p/commit/45d3c6fff662ddd6938982e7e9309ad5fa2ad8dd
