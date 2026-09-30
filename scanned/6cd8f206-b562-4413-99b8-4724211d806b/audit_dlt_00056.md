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

TBD.

Replace the `assert_eq!` with an `Entry`-based check that returns `ValidateContextError::DuplicateTransaction` instead of panicking:

```rust
match self.tx_loc_by_hash.entry(transaction_hash) {
    Entry::Vacant(entry) => {
        entry.insert(transaction_location);
    }
    Entry::Occupied(_) => {
        return Err(ValidateContextError::DuplicateTransaction { transaction_hash });
    }
}
```

### Workarounds

There is no configuration-level workaround. The assert is in the non-finalized state push path, which is exercised by all block processing past the checkpoint height.

### Impact

A malicious block producer can crash targeted Zebra nodes. There are two attack models:

In the first model, the attacker mines two consecutive valid-work blocks where the child repeats a shielded transaction from the parent. At 10% hashrate, the attacker has approximately 11.5 opportunities per day; at 5%, approximately 2.9 per day; at 1%, approximately one every 8.7 days.

In the second model, the attacker broadcasts a shielded transaction into the mempool and waits for any honest miner to include it. The attacker then only needs to mine the next block containing the same transaction. This is cheaper because the attacker does not need to mine the parent block. At 10% hashrate, the attacker has approximately 14.4 single-block opportunities per day; at 5%, approximately 7.2 per day; at 1%, approximately 1.4 per day.

The crash is a process abort (not recoverable within the process). The node must be restarted. Repeated attacks can keep a node down for extended periods. This is a liveness issue, not a consensus divergence: zcashd cleanly rejects the invalid child block while Zebra aborts.

### Credit

Reported by `@haxatron` via email disclosure.

### References

- [CWE-617: Reachable Assertion](https://cwe.mitre.org/data/definitions/617.html)
- [CWE-696: Incorrect Behavior Order](https://cwe.mitre.org/data/definitions/696.html)
- [Zebra `zebra-state/src/service/non_finalized_state/chain.rs` at `d4cd662c`](https://github.com/ZcashFoundation/zebra/blob/d4cd662c716382f6397d2a730148025a1ca79fec/zebra-state/src/service/non_finalized_state/chain.rs#L1608-L1628). Affected assert site.
- [Zebra `zebra-consensus/src/transaction.rs` at `d4cd662c`](https://github.com/ZcashFoundation/zebra/blob/d4cd662c716382f6397d2a730148025a1ca79fec/zebra-consensus/src/transaction.rs#L521-L526). Mempool-only nullifier query gate.
- [Zebra `Cargo.toml` at `d4cd662c`](https://github.com/ZcashFoundation/zebra/blob/d4cd662c716382f6397d2a730148025a1ca79fec/Cargo.toml#L304-L305). `panic = "abort"` in release profile.
