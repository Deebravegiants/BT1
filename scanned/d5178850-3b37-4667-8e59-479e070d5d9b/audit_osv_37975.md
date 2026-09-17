# [H] network-libp2p: Peer can crash the node by opening discovery protocol substream twice

## Summary
Severity: High
Advisory: CVE-2026-34063
Aliases: GHSA-74hp-mhfx-m45h
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-34063
Type: osv

## Details
Nimiq's network-libp2p is a Nimiq network implementation based on libp2p. Prior to version 1.3.0, `network-libp2p` discovery uses a libp2p `ConnectionHandler` state machine. the handler assumes there is at most one inbound and one outbound discovery substream per connection. if a remote peer opens/negotiate the discovery protocol substream a second time on the same connection, the handler hits a `panic!(\"Inbound already connected\")` / `panic!(\"Outbound already connected\")` path instead of failing closed. This causes a remote crash of the networking task (swarm), taking the node's p2p networking offline until restart. The patch for this vulnerability is formally released as part of v1.3.0. No known workarounds are available.

## References
- https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34063.json
- https://github.com/nimiq/core-rs-albatross/security/advisories/GHSA-74hp-mhfx-m45h
- https://nvd.nist.gov/vuln/detail/CVE-2026-34063
- https://github.com/nimiq/core-rs-albatross/commit/e0d4e01994f061bf41d3c2835bc74040d3c084f5
- https://github.com/nimiq/core-rs-albatross/pull/3666
