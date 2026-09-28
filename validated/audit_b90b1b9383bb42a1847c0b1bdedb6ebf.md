### Title
Div-before-mul pro-rata rounding in `calculate_seized_collateral` shrinks every seizure leg below the quote, leaving collateral the liquidator paid for unseized - (contracts/controller/src/positions/liquidation/math.rs)

### Summary
In the controller liquidation path, the pro-rata share of each collateral leg is computed as `asset_value.div(total_collateral)` (an early division), and only then multiplied by `total_seizure_usd`. This is the same bug class as `getClaimableFlux`: flooring an intermediate division before the final multiplication loses precision per leg, so the sum of seized legs is strictly less than `repay_usd * (1 + bonus)`. The liquidator's full repayment is kept while part of the entitled collateral stays in the borrower's position — a permanent, non-recoverable loss of liquidation proceeds for the unprivileged liquidator.

### Finding Description
`build_liquidation_plan` in `contracts/controller/src/positions/liquidation/plan.rs` calls `calculate_seized_collateral` (math.rs:363). For each supply position:

```rust
let share = asset_value.div(env, total_collateral);            // early division, rounds half-up per Wad::div
let seizure_for_asset_usd = total_seizure_usd.mul(env, share); // multiply on the result of division
let seizure_amount_wad = seizure_for_asset_usd.div(env, feed.price); // another div before more rounding
let mut seizure_ray = seizure_amount_wad.to_ray(env);
```

Correct algebra is `floor(seizure_for_asset_usd * asset_value / (total_collateral * price))` — a single `mul_div` per leg. Instead the code chains `div` → `mul` → `div` → `to_asset_floor`, compounding truncation at each step for every collateral leg.

The repayment side has no matching shrinkage: `normalize_repayment_plan` keeps each repayment leg at its ceiling-rounded cap (`actual_debt` via `unscale_borrow_ceil`, math.rs:132), and `release_unbacked_repayment` only trims repayment for `unseized_usd` returned by the low-decimals whole-unit branch (math.rs:401-417). Rounding loss on ordinary legs (decimals ≥ 3, `seizure_ray < actual_ray` not triggered) is never refunded to the liquidator — `unbacked_usd` is only accumulated inside the sub-3-decimal branch, so the general div-then-mul shortfall is silently absorbed.

The same pattern appears in `get_account_bonus_params` (math.rs:590-596): `weight = value.div(total_collateral)` then `weight.mul(bonus)` summed per leg, shrinking the base bonus, and in `calculate_seizure_proportions` (math.rs:91) feeding `proportion_seized`.

### Impact Explanation
An unprivileged liquidator calling `liquidate` on a multi-collateral account pays the full quoted repayment but receives collateral worth strictly less than `repay_usd * (1 + bonus)` — the exact "less reward than entitled" class from the reference report. The unseized value remains in the borrower's supply positions; there is no entrypoint to recover it for the liquidator. Loss scales with the number of collateral legs and is deterministic whenever leg values don't divide `total_collateral` exactly — the common case with mixed assets/decimals.

### Likelihood Explanation
Reachable by any unprivileged address via `liquidate` on any account with `health_factor < 1 WAD` and more than one supply position (or a single leg with non-exact arithmetic). No privileged parameters, oracle honesty assumptions, or timing requirements are needed — every partial liquidation over fractional ratios floors the intermediate `share` and each subsequent conversion.

### Recommendation
Replace the chained `div`/`mul` in `calculate_seized_collateral` with a single `mul_div` per leg: `seizure_ray = mul_div_floor(total_seizure_ray, actual/asset_value_ray, total_collateral_ray_scaled_by_price)` — perform all multiplications before one final division per leg. Apply the same fix to the weight accumulation in `get_account_bonus_params` (`sum of value * bonus` divided once by `total_collateral`). Alternatively, measure the aggregate shortfall between kept `repay_usd * (1+bonus)` and the summed floored seizures and feed it through the existing `unbacked_usd` → `release_unbacked_repayment` path so the liquidator is refunded for collateral the rounding cannot deliver.

### Proof of Concept
Setup: borrower with two 7-decimal supply positions in distinct hub assets, `total_collateral` such that `asset_value / total_collateral` is non-terminating (e.g., leg values 1 USD and 2 USD against total 3 USD → share = 333…333 WAD/leg).

- Leg A: `share = floor(1e18 * 1e18 / 3e18) = 333333333333333333`; `seizure_A = floor(quote * 333333333333333333 / 1e18)` loses up to ~1 unit of `quote` per leg vs. exact `quote / 3`.
- With N legs, each `share` truncation and each subsequent `div(feed.price)` / `to_asset_floor` truncates again; the summed seized USD < `repay_usd * (1+bonus)`, while `repay_usd` is unchanged because `unseized_usd` is only populated in the `asset_decimals < MIN_BORROWABLE_ASSET_DECIMALS` branch.
- A liquidator submitting `liquidate` with `raw_payments` covering the full quote keeps paying `repay_usd` and forfeits the per-leg truncation delta, which stays locked in the borrower's positions.

Analogous to the report's `2.9999999999999989116e22` vs `3e22` delta, the fix is regrouping to multiply-before-divide per leg.