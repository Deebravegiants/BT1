# [H] Resource exhaustion in github.com/libp2p/go-libp2p

## Summary
Severity: High
Advisory: GO-2022-1148
Aliases: CVE-2022-23492, GHSA-j7qp-mfxf-8xjw
Package: github.com/libp2p/go-libp2p
Published: 2022-12-14
Source: https://osv.dev/vulnerability/GO-2022-1148
Type: chain-advisory

## Affected
- Go: `github.com/libp2p/go-libp2p` — affected >=0 <0.18.0

## Details
go-libp2p is vulnerable to targeted resource exhaustion attacks.

These attacks target libp2p's connection, stream, peer, and memory management. An attacker can cause the allocation of large amounts of memory ultimately leading to the process getting killed by the host's operating system.

While a connection manager tasked with keeping the number of connections within manageable limits has been part of go-libp2p, this component was designed to handle the regular churn of peers, not a targeted resource exhaustion attack.

It's recommend to update to v0.21.0 onwards to get some useful functionality that will help in production environments like better metrics around resource usage, Grafana dashboards around resource usage, allow list support, and default autoscaling limits.

## References
- https://github.com/libp2p/go-libp2p/security/advisories/GHSA-j7qp-mfxf-8xjw
- https://github.com/libp2p/go-libp2p/commit/15d7dfbf54264ead8e6f49ca658d79c90635e2de
