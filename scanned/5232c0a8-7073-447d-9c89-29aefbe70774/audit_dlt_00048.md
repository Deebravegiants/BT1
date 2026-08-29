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


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-4g24-549m-hp75_
