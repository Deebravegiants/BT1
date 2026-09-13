# [M] nimiq/core-rs-albatross: Macro block proposal interlink bug

## Summary
Severity: Medium
Advisory: CVE-2026-34061
Aliases: GHSA-gr83-j5f8-p2r5
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-34061
Type: osv

## Details
nimiq/core-rs-albatross is a Rust implementation of the Nimiq Proof-of-Stake protocol based on the Albatross consensus algorithm. Prior to version 1.3.0, an elected validator proposer can send an election macro block whose header.interlink does not match the canonical next interlink. Honest validators accept that proposal in verify_macro_block_proposal() because the proposal path validates header shape, successor relation, proposer, body root, and state, but never checks the interlink binding for election blocks. The same finalized block is later rejected by verify_block() during push with InvalidInterlink. Because validators prevote and precommit the malformed header hash itself, the failure happens after Tendermint decides the block, not before voting. This issue has been patched in version 1.3.0.

## References
- https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34061.json
- https://github.com/nimiq/core-rs-albatross/security/advisories/GHSA-gr83-j5f8-p2r5
- https://nvd.nist.gov/vuln/detail/CVE-2026-34061
- https://github.com/nimiq/core-rs-albatross/commit/9d7d17c9163384e79f61cdbbfe9853ae57bb8bf7
- https://github.com/nimiq/core-rs-albatross/pull/3668
