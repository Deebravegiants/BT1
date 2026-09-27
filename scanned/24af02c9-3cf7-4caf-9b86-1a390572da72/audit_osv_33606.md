# [H] nimiq-network-libp2p Uncontrolled Resource Consumption vulnerability

## Summary
Severity: High
Advisory: CVE-2025-47270
Aliases: GHSA-3v6r-9cr8-q433
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-12
Source: https://osv.dev/vulnerability/CVE-2025-47270
Type: osv

## Details
nimiq/core-rs-albatross is a Rust implementation of the Nimiq Proof-of-Stake protocol based on the Albatross consensus algorithm. The `nimiq-network-libp2p` subcrate of nimiq/core-rs-albatross is vulnerable to a Denial of Service (DoS) attack due to uncontrolled memory allocation. Specifically, the implementation of the `Discovery` network message handling allocates a buffer based on a length value provided by the peer, without enforcing an upper bound. Since this length is a `u32`, a peer can trigger allocations of up to 4 GB, potentially leading to memory exhaustion and node crashes. As Discovery messages are regularly exchanged for peer discovery, this vulnerability can be exploited repeatedly. The patch for this vulnerability is formally released as part of v1.1.0. The patch implements a limit to the discovery message size of 1 MB and also resizes the message buffer size incrementally as the data is read. No known workarounds are available.

## References
- https://github.com/nimiq/core-rs-albatross/releases/tag/v1.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47270.json
- https://github.com/nimiq/core-rs-albatross/security/advisories/GHSA-3v6r-9cr8-q433
- https://nvd.nist.gov/vuln/detail/CVE-2025-47270
- https://github.com/nimiq/core-rs-albatross/commit/566935f0dd0fb41bba1f406d8e3a02dc499520b5
- https://github.com/nimiq/core-rs-albatross/pull/3384
