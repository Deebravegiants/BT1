### Title
Liquidators receive an inflated liquidation bonus because per-collateral weights are rounded half-up before aggregation - (File: contracts/controller/src/positions/liquidation/math.rs)

### Summary
`get_account_bonus_params` independently rounds each collateral leg’s USD weight and bonus contribution using half-up arithmetic, then sums the rounded contributions. An account with multiple collateral positions can therefore produce a weighted liquidation bonus above the true weighted average. The inflated bonus increases `total_seizure_usd` during liquidation, allowing a liquidator to seize more collateral than the configured liquidation bonus permits.

### Finding Description
In `get_account_bonus_params`, each collateral leg calculates:

```rust
let weight = value.div(env, total_collateral);
weighted_bonus_sum += weight.mul(env, Wad::from(position.liquidation_bonus.raw())).raw();
```

`Wad::div` rounds half-up rather than truncating, and the subsequent `Wad::mul` also rounds half-up. The intended weighted bonus is conceptually:

```text
base_bonus = Σ(collateral_value_i × liquidation_bonus_i) / total_collateral
```

The implementation instead computes:

```text
base_bonus = Σ(half_up(half_up(collateral_value_i / total_collateral)
                     × liquidation_bonus_i))
```

Each leg can independently contribute up to half a BPS of positive rounding error. With enough collateral legs, those errors accumulate into a material bonus increase before the result is capped by `max_bonus_for_threshold`.

This is the same incorrect allocation pattern as non-truncated pool fractions: each recipient’s fractional share can be rounded upward independently, making the total allocation exceed the mathematically intended value.

### Impact Explanation
An unprivileged liquidator can receive collateral worth more than the repayment plus the correctly weighted liquidation bonus. The excess is taken from the liquidated account’s collateral rather than from the liquidator’s repayment.

The impact scales with the number of collateral legs:

- Each leg can add up to 0.5 BPS of positive error.
- 200 equal-value legs configured with a 500 BPS bonus can produce a reported base bonus of 600 BPS instead of 500 BPS.
- This is an additional 100 BPS, or 1% of the repayment value, seized by the liquidator.

The resulting loss is borne by the liquidated account and qualifies as theft of user collateral.

### Likelihood Explanation
The attack requires:

- An account with `health_factor < 1 WAD`.
- Multiple collateral positions.
- Enough positions for the accumulated half-up errors to produce a meaningful bonus.
- The inflated base bonus must remain below `max_bonus_for_threshold` or otherwise survive the liquidation curve’s cap.

A liquidator does not need privileged access: liquidation accepts attacker-supplied `raw_payments`, and the inflated bonus is calculated entirely from the victim’s stored collateral positions. The main limitation is that the liquidator cannot manufacture additional collateral positions on another user’s account; exploitation requires targeting an account that already has enough diversified collateral legs.

### Recommendation
Do not round each collateral leg’s normalized weight and bonus contribution independently.

Compute the weighted bonus with one aggregate division:

```rust
weighted_bonus_numerator += collateral_value_i.raw() * liquidation_bonus_i.raw();
base_bonus = floor(weighted_bonus_numerator / total_collateral.raw());
```

Use a sufficiently wide intermediate or checked/I256 multiplication for the numerator. Floor rounding is preferable because an overestimated liquidation bonus pays the liquidator at the borrower’s expense.

The same review should ensure the collateral `share = asset_value.div(env, total_collateral)` calculation cannot overallocate seizure value across legs; a pro-rata allocation should either floor each allocation or reserve any positive remainder rather than letting independently rounded shares sum above one.

### Proof of Concept
Assume:

- 200 collateral positions.
- Each position has the same USD value.
- Each stored `liquidation_bonus` is 500 BPS.
- The threshold-derived maximum bonus is above 600 BPS.
- The account is liquidatable.

For each leg:

```text
weight_i = 1 / 200 = 0.005 WAD
contribution_i = half_up(0.005 × 500) = half_up(2.5) = 3 BPS
```

The implementation sums the independently rounded contributions:

```text
weighted_bonus_sum = 200 × 3 = 600 BPS
```

The true weighted bonus is:

```text
Σ(0.005 × 500) = 500 BPS
```

Thus `bounds.base` is inflated by 100 BPS. During `liquidate`, `estimate_liquidation_amount` can preserve that inflated base bonus, and `calculate_seized_collateral` computes:

```text
total_seizure_usd = repay_usd × (1 + bonus)
```

The liquidator therefore seizes approximately 1% more collateral than intended for the same repayment.