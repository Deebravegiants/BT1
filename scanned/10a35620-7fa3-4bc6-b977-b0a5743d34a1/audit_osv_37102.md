# [H] nimiq/core-rs-albatross's nimiq-blockchain missing proposal body root verification

## Summary
Severity: High
Advisory: CVE-2026-28402
Aliases: GHSA-7wh6-rmxx-ww47
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28402
Type: osv

## Details
nimiq/core-rs-albatross is a Rust implementation of the Nimiq Proof-of-Stake protocol based on the Albatross consensus algorithm. Prior to version 1.2.2, a malicious or compromised validator that is elected as proposer can publish a macro block proposal where `header.body_root` does not match the actual macro body hash. The proposal can pass proposal verification because the macro proposal verification path validates the header but does not validate the binding `body_root == hash(body)`; later code expects this binding and may panic on mismatch, crashing validators. Note that the impact is only for validator nodes. The patch for this vulnerability is formally released as part of v1.2.2. The patch adds the corresponding body root verification in the proposal checks. No known workarounds are available.

## References
- https://github.com/nimiq/core-rs-albatross/releases/tag/v1.2.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28402.json
- https://github.com/nimiq/core-rs-albatross/security/advisories/GHSA-7wh6-rmxx-ww47
- https://nvd.nist.gov/vuln/detail/CVE-2026-28402
- https://github.com/nimiq/core-rs-albatross/commit/6454c26d966858c5520f55739a30b94c17656c85
- https://github.com/nimiq/core-rs-albatross/pull/3623
