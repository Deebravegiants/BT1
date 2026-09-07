# [M] set_weights / commit_weights family is Pays::No with the per-neuron rate limit enforced only in the dispatch body, enabling fee-free block-fill flooding

## Summary
Severity: Medium
Chain: Bittensor
Component: opentensor/subtensor
CWE: Allocation of Resources Without Limits or Throttling
Published: 2026-06-17
Source: https://github.com/RaoFoundation/subtensor/security/advisories/GHSA-h98r-p37h-h4mv
Type: github-advisory

## Details
## Summary

The entire `set_weights` / `commit_weights` / `reveal_weights` family of extrinsics is declared `Pays::No` with an accurately-benchmarked `DispatchClass::Normal` weight. The transaction-validity `SignedExtension` (`SubtensorTransactionExtension::validate`) gates these calls **only** on `check_weights_min_stake` — a one-time minimum-stake check. The per-neuron weight-setting rate limit (`WeightsSetRateLimit`, default 100 blocks) is enforced **only inside the dispatch body** via `ensure!`, which returns an error but, because the call is `Pays::No` and returns a plain `DispatchResult` with no `actual_weight` refund, still consumes the full ~16.9 billion ps of benchmarked block weight for **zero fee**.

A single account holding one min-stake UID can therefore pack a block with many over-rate `set_weights` transactions: all pass `validate`, all are included free, the first succeeds and the rest fail rate-limiting at execution — each burning its declared Normal-class weight at no cost. The result is a fee-free block-fill / congestion primitive against the Normal dispatch class (transfers, staking, etc.). This is the same pattern the maintainers already defend against in `validate` for `register_network`, `serve_axon`, and `associate_evm_key`; the omission for weights is an inconsistency, not a deliberate design.

## Details

### 1. The weight calls are `Pays::No`, `Normal`, accurately benchmarked

`pallets/subtensor/src/macros/dispatches.rs:84-85`:

```rust
#[pallet::call_index(0)]
#[pallet::weight((<T as crate::pallet::Config>::WeightInfo::set_weights(), DispatchClass::Normal, Pays::No))]
pub fn set_weights(
```

The benchmarked weight is large and non-trivial — `pallets/subtensor/src/weights.rs:2617-2625`:

```rust
fn set_weights() -> Weight {
    // Minimum execution time: 16_598_698_000 picoseconds.
    Weight::from_parts(16_897_861_000, 10327382)
        .saturating_add(RocksDbWeight::get().reads(4112_u64))
        .saturating_add(RocksDbWeight::get().writes(2_u64))
}
```

The same `(WeightInfo::…, DispatchClass::Normal, Pays::No)` shape is repeated across the whole family: `set_mechanism_weights` (dispatches.rs:161-164), `batch_set_weights` (205-206), `commit_weights` (235-236), `commit_mechanism_weights` (267-270), `batch_commit_weights` (302-303), `reveal_weights` (349-350), `reveal_mechanism_weights` (402-405), `batch_reveal_weights` (560-561), `commit_crv3_mechanism_weights` (500-503), `commit_timelocked_weights` (2019-2020), `commit_timelocked_mechanism_weights` (2120-2123).

### 2. `validate` gates only on minimum stake, never on the rate limit

`pallets/subtensor/src/extensions/subtensor.rs:244-251` (representative of the family):

```rust
Some(Call::set_weights { netuid, .. })
| Some(Call::set_mechanism_weights { netuid, .. }) => {
```

_Trimmed to 38 lines — full report: https://github.com/RaoFoundation/subtensor/security/advisories/GHSA-h98r-p37h-h4mv_
