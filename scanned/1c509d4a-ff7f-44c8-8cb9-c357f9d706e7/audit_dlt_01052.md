# [M] nimiq-blockchain: Genesis batch set request

## Summary
Severity: Medium
Chain: nimiq-blockchain
Component: nimiq-blockchain
CVE: CVE-2026-46543
CWE: Reachable Assertion
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-vghx-352f-93jm
Type: github-advisory

## Details
### Impact
A remote peer can crash any full node by sending a RequestBatchSet message containing the genesis block's hash. The handler calls `get_epoch_chunks` which iterates backwards through macro blocks using `Policy::macro_block_before`. When it reaches the genesis block number, `macro_block_before` panics with "No macro blocks before genesis block".

### Patches
[The patch for this vulnerability](https://github.com/nimiq/core-rs-albatross/pull/3745) is formally released as part of [v1.5.0](https://github.com/nimiq/core-rs-albatross/releases/tag/v1.5.0).

### Workarounds
No Workaround, although requesting the genesis batch set is not used during normal operation.

### Resources
See [PR](https://github.com/nimiq/core-rs-albatross/pull/3745).
