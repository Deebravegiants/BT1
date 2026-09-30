# [H] nimiq/core-rs-albatross: Discovery handshake limit could underflow and later provoke a deterministic overflow panic

## Summary
Severity: High
Advisory: CVE-2026-33184
Aliases: GHSA-5rm9-893q-vmhm
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-33184
Type: osv

## Details
nimiq/core-rs-albatross is a Rust implementation of the Nimiq Proof-of-Stake protocol based on the Albatross consensus algorithm. Prior to version 1.3.0, the discovery handler accepts a peer-controlled limit during handshake and stores it unchanged. The immediate HandshakeAck path then honors limit = 0 and returns zero contacts, which makes the session look benign. Later, after the same session reaches Established, the periodic update path computes self.peer_list_limit.unwrap() as usize - 1. With limit = 0, that wraps to usize::MAX and then in rand 0.9.2, choose_multiple() immediately attempts Vec::with_capacity(amount), which deterministically panics with capacity overflow. This issue has been patched in version 1.3.0.

## References
- https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33184.json
- https://github.com/nimiq/core-rs-albatross/security/advisories/GHSA-5rm9-893q-vmhm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33184
- https://github.com/nimiq/core-rs-albatross/commit/8f60a2d75b74b55764ecf34bd4435f4961630595
- https://github.com/nimiq/core-rs-albatross/pull/3664
