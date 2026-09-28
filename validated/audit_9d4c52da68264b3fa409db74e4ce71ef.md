### Title
Liquidation can execute with a non-empty repayment and an empty seizure — the liquidator pays real debt tokens and receives nothing - (File: contracts/controller/src/positions/liquidation/mod.rs)

### Summary

The analog of "zero `seizeInternal` succeeds while doing nothing" exists in `process_liquidation` in a stronger form: the execution path validates only that the normalized `repaid` vector is non-empty (`require_non_empty_payments(env, &result.repaid)` at `mod.rs:66`), but never requires the `seized` vector to be non-empty. When every collateral leg's seizure rounds to zero and is dropped by `calculate_seized_collateral`, the plan still carries the positive repayment legs, the liquidator's tokens are pulled into the pool, the borrower's debt is burned, and no collateral moves. A `LiquidationEvent` with `repaid_usd_wad > 0` is emitted — a real payment settled against an "empty" seizure.

### Finding Description

In `plan::build_liquidation_plan` (`contracts/controller/src/positions/liquidation/plan.rs:73-79`), zero-seizure legs are dropped in `calculate_seized_collateral` (`math.rs:419-430`: `if seizure_ray <= Ray::ZERO { continue; }` and `if capped_ray <= Ray::ZERO { continue; }`). The repayment is only released for two cases:

- `unbacked_usd` accumulated by the sub-3-decimal whole-unit flooring branch (`math.rs:408-416`), and
- the special case `unbacked_usd > 0 && seized_collaterals.is_empty()` which releases the whole repayment (`plan.rs:76-79`).

For legs dropped through the generic `seizure_ray <= 0` / `capped_ray <= 0` paths — e.g., a dust-size repayment whose `seizure_usd` rounds to zero RAY on every supply position — no `unbacked_usd` is recorded, so `release_unbacked_repayment` removes nothing and `repayment.repaid` keeps the positive legs. `LiquidationPlan::validate` (`math.rs:54-69`) iterates `self.seized` and is vacuously satisfied by an empty vector.

`process_liquidation` then:

1. Passes `require_non_empty_payments(env, &result.repaid)` (`mod.rs:66`) because `repaid` is non-empty.
2. Calls `apply::apply_liquidation_repayments` (`mod.rs:68-75`), which pulls the liquidator's debt-token transfers into the pool and burns the borrower's debt shares.
3. Calls `scale_seizures_to_received` on the empty `result.seized` (`mod.rs:79`) and applies an empty seizure loop (`mod.rs:80-94`) — no tokens paid out, no shares credited.
4. Emits `LiquidationEvent` (`mod.rs:97-103`) with the measured `repaid_usd_wad` and publishes position updates reflecting the reduced debt.

The protocol's own integration guidance documents this acceptance explicitly: "Reject an estimate whose `seized_collaterals` is empty. The contract accepts a liquidation that repays debt and seizes nothing, so the liquidator would pay and receive no collateral" (`skills/xoxno-lending-liquidations/SKILL.md:178-180`).

### Impact Explanation

Permanent loss of the liquidator's funds with a direct transfer of value to the borrower: the pulled repayment tokens reduce the liquidated account's debt (increasing its health factor) while the liquidator receives zero collateral and zero bonus. Unlike the Cream analog (a wasted no-op), here real tokens change hands — the borrower's debt is repaid for free. A borrower can deliberately construct a dust-value, below-HF position (tiny collateral relative to a dust debt, or collateral priced so that a small repayment's seizure rounds to zero RAY) that bait liquidator bots which call `liquidate` without gating on the estimate; each such call donates the repayment to the borrower's account. This is theft/loss of user funds reachable by any unprivileged liquidator call and profitably triggerable by an unprivileged borrower.

### Likelihood Explanation

Requires no privileged action: any address can open a minimal borrow position, let interest accrue until `HF < 1`, and leave collateral whose per-leg `seizure_ray` floors to zero for small offers. Liquidator bots that execute without simulating `get_liquidation_estimate` and rejecting empty `seized_collaterals` will be drained. The amounts per call are bounded by the dust repayment that still produces a zero seizure, but the pattern is repeatable and the borrower's gain (free debt repayment plus improved HF) is guaranteed whenever triggered. Severity is capped at Medium: losses are self-inflicted by the calling liquidator and individually small.

### Recommendation

Mirror the suggested fix — quit after checks when the seizure is empty. In `process_liquidation` (or at the end of `build_liquidation_plan`), after `calculate_seized_collateral` and `release_unbacked_repayment`, reject a plan whose seizure is empty while its repayment is not:

```rust
// plan.rs, after release_unbacked_repayment
assert_with_error!(
    env,
    !seized_collaterals.is_empty() || repayment.repaid.is_empty(),
    GenericError::InvalidPayments
);
```

Equivalently, in `LiquidationPlan::validate` or `process_liquidation`, require `!result.seized.is_empty()` whenever `result.repaid` is non-empty, so a liquidation that takes payment always delivers collateral — matching the upstream recommendation to return early instead of settling an empty seize.

### Proof of Concept

1. Borrower opens a position: supplies a small amount of collateral `X` and borrows a dust amount of debt token `D`, then waits/accrues until `health_factor < Wad::ONE` (`plan.rs:40-44` passes).
2. Liquidator calls `controller.liquidate(liquidator, account_id, [(hub_asset_D, tiny_amount)], SeizeMode::Transfer)` where `tiny_amount` is positive but its USD value, divided across the collateral legs by `calculate_seized_collateral`, produces `seizure_ray <= 0` (or `capped_ray <= 0`) on every leg (`math.rs:419-430`). The liquidator authorizes `transfer(liquidator, pool, tiny_amount)`.
3. All seizure legs are dropped; `unbacked_usd == 0`, so `repayment.repaid` retains the positive leg (`plan.rs:73-79`).
4. `require_non_empty_payments(&result.repaid)` passes (`mod.rs:66`); `apply_liquidation_repayments` pulls `tiny_amount` of `D` from the liquidator to the pool and reduces the borrower's debt shares; `scale_seizures_to_received`/`apply_liquidation_seizures` iterate an empty vector — zero collateral leaves the account.
5. `LiquidationEvent` publishes `repaid_usd_wad > 0`; the borrower's debt decreased and HF improved; the liquidator's balance decreased by `tiny_amount` with no collateral received. `get_liquidation_estimate` for the same inputs would have shown `seized_collaterals.is_empty()` — which the protocol's own SKILL.md tells integrators to reject because the contract executes it anyway.