# [M] nimiq-blockchain: Peer-triggerable panic during history sync

## Summary
Severity: Medium
Chain: nimiq-blockchain
Component: nimiq-blockchain
CVE: CVE-2026-34066
CWE: Improper Input Validation, Reachable Assertion, Improper Check for Unusual or Exceptional Conditions
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-j99g-7rqw-q9jg
Type: github-advisory

## Details
### Impact
`HistoryStore::put_historic_txns` uses an `assert!` to enforce invariants about `HistoricTransaction.block_number` (must be within the macro block being pushed and within the same epoch). During history sync, a peer can influence the `history: &[HistoricTransaction]` input passed into `Blockchain::push_history_sync`, and a malformed history list can violate these invariants and trigger a panic.

`extend_history_sync` calls `this.history_store.add_to_history(..)` before comparing the computed history root against the macro block header (`block.history_root()`), so the panic can happen before later rejection checks run.

### Patches
[The patch for this vulnerability](https://github.com/nimiq/core-rs-albatross/commit/6f5511309c199d84b012fe6b9aba7e5582892c50) is included as part of [v1.3.0](https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0).

### Workarounds
No known workarounds.
