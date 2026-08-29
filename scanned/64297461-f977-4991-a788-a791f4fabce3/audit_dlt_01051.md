# [H] nimiq-primitives: Panic DoS in trie chunk processing via ROOT-keyed item

## Summary
Severity: High
Chain: nimiq-primitives
Component: nimiq-primitives
CVE: CVE-2026-46545
CWE: Uncaught Exception
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-mw3q-r9wh-h2ff
Type: github-advisory

## Details
### Impact

A remote, unauthenticated denial-of-service vulnerability in `MerkleRadixTrie::put_chunk` allows any state-sync peer to crash any node performing state synchronization (freshly joining nodes and recovering nodes).

A malicious peer can respond to a `RequestChunk` with a `ResponseChunk::Chunk` whose first `TrieItem.key` is the empty (ROOT) key. The chunk passes sorting, range, and Merkle-proof validation, but when `put_raw` tries to store a value at the root node, it calls `TrieNode::put_value(...).unwrap()`, which returns `Err(RootCantHaveValue)` and panics, aborting the node process. The panic fires on the first malicious chunk the victim commits; no rate limit or authentication gate caps the attack.

Impacted: any node running state sync against untrusted peers — this includes fresh nodes performing initial download and existing nodes recovering from data loss. Honest nodes never construct ROOT-keyed items, so non-syncing operation is unaffected.

### Patches

See [PR](https://github.com/nimiq/core-rs-albatross/pull/3762).

### Workarounds

There is no safe in-process workaround: any peer serving state-sync data can trigger the crash and the code path is not guarded by a feature flag.

### Resources

- Fix commit: (link to the merged PR commit, once merged)
- Affected code: [`primitives/trie/src/trie.rs`](https://github.com/nimiq/core-rs-albatross/blob/albatross/primitives/trie/src/trie.rs) — `put_chunk` (around line 819) and `put_raw` (around line 351)
