# [M] Quadratic transparent value check in block contextual verification

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-17
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-4g24-549m-hp75
Type: github-advisory

## Details
# Quadratic transparent value check in block contextual verification

| Field | Value |
|---|---|
| Severity | Moderate |
| CVSS 3.1 | AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (5.9) |
| CWE | CWE-407 (Inefficient Algorithmic Complexity) / CWE-405 (Asymmetric Resource Consumption) |
| Affected versions | through v6.0.0 |
| Patched versions | 6.1.0 |
| Reporter credit | Partner disclosure (@ebfull and @ValarDragon ) |
| Fix PR | #10995 |

## Am I affected?

You are affected if you run an affected version and validate blocks (all default full-node configurations). The condition is triggered by a specific worst-case block, and that block must carry valid proof-of-work to reach the affected code, so it cannot be induced by an arbitrary unauthenticated peer sending an unmined block. The block can be produced either by an attacker who mines it, or by seeding the public mempool so an honest miner mines it; either way the proof-of-work requirement holds and the mempool itself is not slowed. The impact is a one-time processing stall (measured at over 52 seconds on fast hardware, longer on slower nodes) while the malicious block is validated. There is no crash, no consensus divergence, and no state corruption.

## Summary

When Zebra validates a block during contextual verification, it checks the remaining transparent value of every non-coinbase transaction. The current implementation clones and converts the entire block-level spent-UTXO map once per transaction (twice, in fact, because the value-balance conversion clones it again), rather than passing each transaction only the outputs it spends. For a block near the 2,000,000 byte limit packed with minimal single-input transactions (up to roughly 26,000), this turns a linear-time value check into quadratic hashmap allocation and copying, measured at over 52 seconds of processing for a single block. Because the affected code runs only after proof-of-work and other semantic checks pass, triggering it requires producing a valid mined block, which bounds who can cause it and at what cost.

## Details

Verified on v6.0.0.

`transparent_spend` (`zebra-state/src/service/check/utxo.rs:38`) builds one block-level map of all transparent outputs spent anywhere in the block:

```rust
let mut block_spends = HashMap::new();
// ... for every input of every transaction, insert (outpoint -> OrderedUtxo) ...
remaining_transaction_value(semantically_verified, &block_spends)?;   // utxo.rs:94
```

`remaining_transaction_value` (utxo.rs:231) then iterates every non-coinbase transaction and, on each iteration, clones and converts that whole block-level map:

```rust
let value_balance = transaction.value_balance(&utxos_from_ordered_utxos(utxos.clone()));  // utxo.rs:244
```

`utxos` is the entire `block_spends` map, so `utxos.clone()` copies all of it per transaction, and `utxos_from_ordered_utxos` (utxo.rs:143) allocates a fresh map of the same size via `into_iter().map().collect()`. `Transaction::value_balance` (`zebra-chain/src/transaction.rs:1565`) then clones the map a second time:

```rust
self.value_balance_from_outputs(&outputs_from_utxos(utxos.clone()))
```

So the per-transaction cost is clone, convert, clone, convert, each over a map whose size is proportional to the number of transparent inputs in the whole block. With N transactions and an O(N)-sized map, total work is O(N^2). A block near the 2,000,000 byte cap can hold roughly 26,000 minimal single-input transactions, giving on the order of 7e8 map-entry operations, measured by the reporter at over 52 seconds on M4 hardware.

The transaction only needs its own spent outputs to compute its value balance, so the correct cost is O(inputs of that transaction), making the whole check O(total inputs), that is linear.

Reachability: this code runs in the state contextual-verification path, reached only via `Request::CommitSemanticallyVerifiedBlock`, which the block verifier issues (`zebra-consensus/src/block.rs:394`) only after `difficulty_is_valid` and `equihash_solution_is_valid` (block.rs:246-247, the proof-of-work checks) and `merkle_root_validity` have passed. A block without valid proof-of-work is rejected earlier for negligible cost and never reaches the quadratic code. The proposal and `disable_pow()` paths (block.rs:241) skip full proof-of-work, but those are template-proposal and regtest paths, not untrusted peer input.

Trigger routes: the worst-case block can be produced either by an attacker who mines it directly, or by seeding the public mempool with the minimal transparent transactions and letting an honest miner assemble and mine them. The mempool itself is not slowed by this (per-transaction mempool verification operates on a map of only that transaction's own inputs, so the block-level quadratic does not occur there); the mempool-seeding route is a cheaper way to cause the same block-validation stall, not a separate vulnerability. It is opportunistic: the attacker does not control which miner includes the transactions or whether they land in a single worst-case block.

ZIP-317 does not mitigate this. The conventional fee (`MARGINAL_FEE` times `max(logical_actions, GRACE_ACTIONS)`) governs mempool eviction and block-production weighting, not structural admission, so a fully fee-paying block of minimal transparent transactions is valid and still triggers the quadratic work. A worst-case block's transactions cost on the order of a few ZEC in conventional fees to seed, and an attacker who mines the block themselves recoups those fees. Because the validation cost is quadratic while the fee is linear in transaction size, no fee level prices the cost correctly until the algorithm is made linear.

## Patches

6.1.0. The fix is to give each transaction only the outputs it spends, rather than cloning the whole block-level map per transaction:

- In `remaining_transaction_value`, build or borrow a per-transaction view containing only that transaction's spent outpoints and pass that to `value_balance`, making the per-transaction cost proportional to that transaction's input count.
- Additionally, avoid the second clone by having `value_balance` / `value_balance_from_outputs` borrow rather than clone-and-convert (transaction.rs:1565).

The change is a performance and allocation fix only. It must not alter which outputs a transaction's value balance is computed over, and must preserve the duplicate-spend and value-balance consensus checks exactly.

## Workarounds

There is no configuration-only workaround; the check runs on the standard block validation path. The proof-of-work requirement limits the attack (an unmined block cannot reach the code) but does not prevent it, since a fee-paying worst-case block can be mined directly or seeded into the mempool for an honest miner to mine, and ZIP-317 fees do not filter it. Upgrading once a patch is available is the durable fix.

## Impact

Availability only, and bounded. An actor can construct one worst-case block, either by mining it directly or by seeding the public mempool with the minimal transparent transactions and letting an honest miner mine them, that costs every validating node over 52 seconds to process, once, for that block. The effect clears when processing completes. It is not amplifiable without a new block per attack, and it does not crash the node, diverge consensus, or corrupt state. The severity depends on whether that processing stall degrades the rest of the node (missed timers, dropped gossip, sync lag) for its duration or is isolated to block processing, which is pending confirmation. The trigger still requires a valid-proof-of-work block to exist: the mempool-seeding route lowers the attacker's cost (fees rather than hashpower, on the order of a few ZEC and opportunistic on miner behaviour) but does not change the impact, and ZIP-317 fees do not prevent it. The bounded, one-time, self-clearing nature of the stall keeps the realistic incentive low.

## Credit

Reported by @ValarDragon and @ebfull, including a measured 52-second worst-case timing and a precise root-cause analysis of the per-transaction map cloning.

## References

- `zebra-state/src/service/check/utxo.rs:38,94,143,231,244` (transparent_spend, remaining_transaction_value, utxos_from_ordered_utxos, the per-transaction clone)
- `zebra-chain/src/transaction.rs:1561,1565` (value_balance, the second clone)
- `zebra-consensus/src/block.rs:241,246,247,257,394` (proof-of-work and merkle checks before the state commit)
- CWE-407, CWE-405
