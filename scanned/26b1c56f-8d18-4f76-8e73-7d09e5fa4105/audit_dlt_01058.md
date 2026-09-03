# [M] nimiq-transaction: UpdateValidator transactions allows voting key change without proof-of-knowledge

## Summary
Severity: Medium
Chain: nimiq-transaction
Component: nimiq-transaction
CVE: CVE-2026-34068
CWE: Improper Verification of Cryptographic Signature
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-pf4j-pf3w-95f9
Type: github-advisory

## Details
### Impact
The staking contract accepts `UpdateValidator` transactions that set `new_voting_key=Some(...)` while omitting `new_proof_of_knowledge`. this skips the proof-of-knowledge requirement that is needed to prevent BLS rogue-key attacks when public keys are aggregated.

Because tendermint macro block justification verification aggregates validator voting keys and verifies a single aggregated BLS signature against that aggregate public key, a rogue-key voting key in the validator set can allow an attacker to forge a quorum-looking justification while only producing a single signature.

While the impact is critical, the exploitability is low: The voting keys are fixed for the epoch, so the attacker would need to know the next epoch validator set (chosen through VRF), which is unlikely.

### Patches
[The patch for this vulnerability](https://github.com/nimiq/core-rs-albatross/commit/e7f0ab7d2115e17d6e5548ddc60f10df1a5d645f) is included as part of [v1.3.0](https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0).

### Workarounds
No known workarounds.
