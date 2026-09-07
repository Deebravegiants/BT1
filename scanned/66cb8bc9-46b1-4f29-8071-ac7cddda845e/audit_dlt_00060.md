# [H] Block suppression via NU5 same-header body poisoning of sent-hash cache

## Summary
Severity: High
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-52736
CWE: Incomplete Cleanup
Published: 2026-05-29
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-4m69-67m6-prqp
Type: github-advisory

## Details
## Description

### Am I affected

You are affected if:

1. You run any version of `zebrad` up to and including `v4.4.1`.
2. Your node accepts inbound P2P connections (`network.listen_addr` is set, which is the default).
3. Your node processes blocks past the checkpoint height (non-finalized state is active).

All default configurations are affected.

### Summary

Zebra records a block hash in `non_finalized_block_write_sent_hashes` when the block is sent to the write task, before contextual validation completes. If validation fails, the hash is not removed. A remote unauthenticated peer can deliver a poisoned block body that shares a header hash with a later valid canonical block. The poisoned body is rejected, but the hash remains cached. When the valid canonical block arrives, Zebra treats it as a duplicate and rejects it. The node cannot advance past that height until restart or a reorg event.

### Details

ZIP-244 defines `txid_v5` without binding transparent input `scriptSig`, which lives in `auth_digest` and is committed to by `hashBlockCommitments` in the block header. Because `merkle_root` is computed over txids (not auth digests), and the block hash is computed over the header, an attacker can construct two blocks with identical header hashes but different transaction bodies by mutating the coinbase scriptSig.

The attack flow over P2P:

1. Attacker observes a new block header (from any peer).
2. Attacker constructs a poisoned body by flipping a byte of the coinbase scriptSig extra-data section. The block hash is unchanged.
3. Attacker advertises the block hash via `inv` to the target node.
4. Target requests the block via `getdata`; attacker serves the poisoned body.
5. Zebra adds the hash to `non_finalized_block_write_sent_hashes` before validation.
6. The write task rejects the body at `block_commitment_is_valid_for_chain_history` (auth_data_root mismatch).
7. The hash is not removed from `non_finalized_block_write_sent_hashes`.
8. When the valid canonical block arrives (from honest peers or RPC), `queue_and_commit_to_non_finalized_state` sees the hash in the cache and returns `KnownBlock::WriteChannel` duplicate.
9. The node is stuck at height N-1.

A secondary variant exists where chain pruning (via `MAX_NON_FINALIZED_CHAIN_FORKS`) removes a chain from `chain_set` but leaves its block hashes in `non_finalized_block_write_sent_hashes`, producing the same lockout for children of the pruned fork.

### Patches

Patched in Zebra 4.4.2. The fix removes stale entries from `non_finalized_block_write_sent_hashes` on every failed non-finalized write path.


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-4m69-67m6-prqp_
