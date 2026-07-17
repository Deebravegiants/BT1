### Title
`get_sortable_validator_online_ratio` Ignores `endorsement_cutoff_threshold`, Producing Incorrect Validator Exemption-from-Kickout Ordering - (File: chain/epoch-manager/src/validator_stats.rs)

### Summary
The function used to sort validators for exemption from kickout (`get_sortable_validator_online_ratio`) always computes the online ratio with `endorsement_cutoff_threshold = None`, while the actual reward calculation — and the protocol's intended semantics — applies a binary cutoff to the endorsement ratio. This formula inconsistency causes the exemption algorithm to overestimate the online ratio of validators whose endorsement rate falls below the cutoff, potentially exempting the wrong validators from kickout and corrupting the next epoch's validator set.

### Finding Description

In `chain/epoch-manager/src/validator_stats.rs`, `get_sortable_validator_online_ratio` is a wrapper that always calls `get_validator_online_ratio(stats, None)`, hardcoding `None` for the endorsement cutoff threshold: [1](#0-0) 

This function is called inside `compute_validators_to_reward_and_kickout` to sort all validators by online ratio, which then drives `compute_exempted_kickout` — the mechanism that prevents too many validators from being kicked out in a single epoch: [2](#0-1) 

However, in `finalize_epoch`, when the reward calculation is performed, the `endorsement_cutoff_threshold` is explicitly set to `Some(epoch_config.chunk_validator_only_kickout_threshold)` (70 in production): [3](#0-2) 

Inside `calculate_reward`, this cutoff is passed to `get_validator_online_ratio`, which remaps the endorsement ratio to 0 (below cutoff) or 1 (at or above cutoff) before computing the average uptime: [4](#0-3) 

The cutoff logic itself is in `get_endorsement_ratio`: [5](#0-4) 

The result is two divergent formulas for the same conceptual quantity ("validator online ratio"):

| Usage | Endorsement contribution |
|---|---|
| Sorting for exemption | Raw ratio (e.g. 40/100 = 0.40) |
| Reward calculation | Binary: 0 if below cutoff, 1 if above |

A chunk-validator-only node with a 40% endorsement rate (below the 70% production cutoff) would have its online ratio computed as `(0 + 0.40) / 2 = 0.20` in the sort, but `(0 + 0) / 2 = 0.00` in the reward formula. The sort overestimates its standing relative to the reward formula.

### Impact Explanation

When `validator_max_kickout_stake_perc` is active (i.e., many validators fall below their kickout thresholds simultaneously), `compute_exempted_kickout` iterates validators from highest to lowest sortable online ratio and exempts them until the retained stake threshold is met.

Because the sort uses the raw endorsement ratio, a chunk-validator-only node with a 40% endorsement rate (below the 70% cutoff) appears to have a higher online ratio than it actually does under the protocol's reward semantics. It may be exempted from kickout ahead of a validator with a genuinely higher cutoff-adjusted online ratio. The result is that the wrong validator is kept in the active set for the next epoch — a validator that the protocol's own reward formula treats as having zero endorsement contribution is retained, while a better-performing validator is ejected.

The corrupted value is the `validator_kickout` map written into `EpochInfo` at epoch finalization, which directly determines the validator set for epoch T+2. [6](#0-5) 

### Likelihood Explanation

The discrepancy only matters when `validator_max_kickout_stake_perc` is binding (i.e., enough validators are simultaneously below their thresholds that the exemption mechanism activates). In production, `validator_max_kickout_stake_perc` is 30, meaning up to 70% of total stake can be kicked out before the exemption kicks in. This is an unusual but plausible condition during network instability. The `endorsement_cutoff_threshold` is set to 70 in all production epoch configs, making the formula divergence concrete and not hypothetical.

### Recommendation

`get_sortable_validator_online_ratio` should accept and forward the `endorsement_cutoff_threshold` parameter so that the sort order used for exemption is computed with the same formula as the reward calculation. Alternatively, the call site in `compute_validators_to_reward_and_kickout` should pass the epoch config's `chunk_validator_only_kickout_threshold` as the cutoff when invoking the sort.

### Proof of Concept

Setup (matching production config):
- `chunk_validator_only_kickout_threshold` = 70
- `validator_max_kickout_stake_perc` = 30
- Two chunk-validator-only nodes, equal stake:
  - **V_A**: endorsement ratio 40% (below cutoff)
  - **V_B**: endorsement ratio 65% (below cutoff)
- Both fail the kickout check; combined stake exceeds the 30% kickout limit, so one must be exempted.

**Current behavior** (sort uses raw ratio):
- V_A sortable ratio = 0.40, V_B sortable ratio = 0.65
- V_B is exempted (higher raw ratio); V_A is kicked out.

**Correct behavior** (sort uses cutoff-adjusted ratio):
- V_A cutoff-adjusted ratio = 0.00, V_B cutoff-adjusted ratio = 0.00
- Tie broken by stake or account ID — the outcome differs from the current code.

The current code exempts V_B (65% endorsement) over V_A (40% endorsement) based on raw ratio, but under the protocol's own reward formula both have an endorsement contribution of 0. The exemption decision is made using a formula that is inconsistent with the protocol's stated semantics, corrupting the `EpochInfo.validator_kickout` DB entry and the resulting validator set for epoch T+2. [7](#0-6) [8](#0-7)

### Citations

**File:** chain/epoch-manager/src/validator_stats.rs (L103-118)
```rust
/// Computes the overall online (uptime) ratio of the validator for sorting.
/// The reason for this function is that U256 used in the core implementation
/// cannot be used with `Ratio<U256>` for sorting since it does not implement `num_integer::Integer`.
/// Instead of having a full-blown implementation of `U256`` for `num_integer::Integer`
/// we wrap the value in a `BigInt` for now.
/// TODO: Implement `num_integer::Integer` for `U256` and remove this function.
/// cspell:words bigdenom bignumer
pub(crate) fn get_sortable_validator_online_ratio(stats: &BlockChunkValidatorStats) -> BigRational {
    let ratio = get_validator_online_ratio(stats, None);
    let mut bytes: [u8; size_of::<U256>()] = [0; size_of::<U256>()];
    ratio.numer().to_little_endian(&mut bytes);
    let bignumer = BigUint::from_bytes_le(&bytes);
    ratio.denom().to_little_endian(&mut bytes);
    let bigdenom = BigUint::from_bytes_le(&bytes);
    BigRational::new(bignumer.try_into().unwrap(), bigdenom.try_into().unwrap())
}
```

**File:** chain/epoch-manager/src/validator_stats.rs (L124-134)
```rust
fn get_endorsement_ratio(stats: &ValidatorStats, cutoff_threshold: Option<u8>) -> (u64, u64) {
    let (numer, denom) = if stats.expected == 0 {
        debug_assert_eq!(stats.produced, 0);
        (0, 0)
    } else if let Some(threshold) = cutoff_threshold {
        if stats.less_than(threshold) { (0, 1) } else { (1, 1) }
    } else {
        (stats.produced, stats.expected)
    };
    (numer, denom)
}
```

**File:** chain/epoch-manager/src/lib.rs (L500-516)
```rust
        let mut sorted_validators = validator_block_chunk_stats
            .iter()
            .map(|(account, stats)| (get_sortable_validator_online_ratio(stats), account))
            .collect_vec();
        sorted_validators.sort_by(validator_comparator);
        let accounts_sorted_by_online_ratio =
            sorted_validators.into_iter().map(|(_, account)| account.clone()).collect_vec();

        let exempt_perc =
            100_u8.checked_sub(config.validator_max_kickout_stake_perc).unwrap_or_default();
        let exempted_validators = Self::compute_exempted_kickout(
            epoch_info,
            &accounts_sorted_by_online_ratio,
            total_stake,
            exempt_perc,
            prev_validator_kickout,
        );
```

**File:** chain/epoch-manager/src/lib.rs (L696-704)
```rust
        let (validator_block_chunk_stats, kickout) = Self::compute_validators_to_reward_and_kickout(
            &config,
            &epoch_info,
            &block_validator_tracker,
            &chunk_validator_tracker,
            &spice_endorsement_tracker,
            prev_validator_kickout,
        );
        validator_kickout.extend(kickout);
```

**File:** chain/epoch-manager/src/lib.rs (L896-904)
```rust
            // We use the chunk validator kickout threshold as the cutoff threshold for the
            // endorsement ratio to remap the ratio to 0 or 1.
            let online_thresholds = ValidatorOnlineThresholds {
                online_min_threshold: epoch_config.online_min_threshold,
                online_max_threshold: epoch_config.online_max_threshold,
                endorsement_cutoff_threshold: Some(
                    epoch_config.chunk_validator_only_kickout_threshold,
                ),
            };
```

**File:** chain/epoch-manager/src/reward_calculator.rs (L94-98)
```rust
        for (account_id, stats) in validator_block_chunk_stats {
            let production_ratio =
                get_validator_online_ratio(&stats, online_thresholds.endorsement_cutoff_threshold);
            let average_produced_numer = production_ratio.numer();
            let average_produced_denom = production_ratio.denom();
```
