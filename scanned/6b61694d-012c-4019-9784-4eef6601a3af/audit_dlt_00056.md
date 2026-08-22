# [M] Repeated Non-Finalized Shielded Transaction Aborts Zebra Before Duplicate-Nullifier Rejection

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-52739
Published: 2026-05-29
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-hhm7-qrv5-h4r6
Type: github-advisory

## Details
### Am I affected

You are affected if:

1. You run `zebrad` up to and including `v4.4.1`.
2. Your node processes blocks past the checkpoint height (non-finalized state is active).
3. The network has NU5 or later activated.

All default configurations are affected.

### Summary

`Chain::push` in the non-finalized state updates the transaction-location index (`tx_loc_by_hash`) before it runs the duplicate shielded-nullifier guard. When an invalid child block repeats a shielded transaction from its non-finalized parent, the `assert_eq!(prior_pair, None, "transactions must be unique within a single chain")` fires before the contextual validation that would cleanly reject the duplicate. Under Zebra's `panic = "abort"` release profile, this terminates the entire node process.

The block should be rejected with a duplicate-nullifier contextual validation error. Instead, the ordering of index updates within `Chain::push` causes the process to abort.

### Details

In `zebra-state/src/service/non_finalized_state/chain.rs:1608-1628`, the block push sequence is:

1. Insert transaction hash into `tx_loc_by_hash` with `assert_eq!` on uniqueness
2. Update transparent outputs and inputs
3. Update shielded data (JoinSplit, Sapling, Orchard) — including nullifier uniqueness checks

The shielded nullifier uniqueness check at step 3 would correctly reject the duplicate transaction. But the `assert_eq!` at step 1 fires first because the transaction hash is already in `tx_loc_by_hash` from the parent block on the same chain.

The block transaction verifier does not run the best-chain nullifier query for block transactions — that check is gated on mempool transactions only (`zebra-consensus/src/transaction.rs:521-526`). Initial contextual validation checks nullifiers in finalized state only (`zebra-state/src/service/check.rs:407-415`), but the parent transaction is still in non-finalized state.

There are two attack models:

**Model A (two attacker blocks):** The attacker mines two consecutive valid-work blocks: parent B1 containing a shielded transaction T, and child B2 repeating T. This requires controlling both blocks consecutively.

**Model B (one attacker block after an honest block):** The attacker broadcasts a shielded transaction T into the mempool. When any honest miner includes T in their block B1, the attacker only needs to mine the next child block B2 containing the same T. This requires controlling only one block immediately after an honest block that included the attacker's transaction. The attacker can broadcast a suitable shielded transaction every block until one is included by an honest miner, then attempt to mine the follow-up.

Both models require the child block to repeat the shielded-only V5 transaction while the parent is still in non-finalized state.

### Patches


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-hhm7-qrv5-h4r6_
