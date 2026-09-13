# [M] Nimiq light-blockchain: Light blockchain rebranch issue

## Summary
Severity: Medium
Advisory: CVE-2026-46540
Aliases: GHSA-m3pg-qc2q-mg8c
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46540
Type: osv

## Details
Nimiq is a Rust implementation of the Nimiq Proof-of-Stake protocol based on the Albatross consensus algorithm. Prior to version 1.4.0, when LightBlockchain::rebranch() adopts a fork chain whose tip is a macro block (checkpoint or election), it only updates self.head but fails to update self.macro_head, self.election_head, self.current_validators, or store the election header in the chain_store. This is in direct contrast with the full Blockchain::rebranch() at blockchain/src/blockchain/push.rs:504-518, which correctly updates all macro/election state when the new head is a macro block. After a rebranch to a macro block, the stale macro_head causes subsequent macro blocks pushed via push() to be verified against the wrong predecessor via verify_macro_successor(&this.macro_head). If the rebranch target was an election block, the stale current_validators causes every subsequent block to fail verify_validators(), completely stalling the light client's chain progression. This issue has been patched in version 1.4.0.

## References
- https://github.com/nimiq/core-rs-albatross/releases/tag/v1.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46540.json
- https://github.com/nimiq/core-rs-albatross/security/advisories/GHSA-m3pg-qc2q-mg8c
- https://nvd.nist.gov/vuln/detail/CVE-2026-46540
- https://github.com/nimiq/core-rs-albatross/pull/3706
