### Title
Unprivileged borrower can freeze all supplier withdrawals by pushing utilization over `max_utilization` - (File: contracts/pool/src/guards.rs)

### Summary
`borrow` enforces `require_utilization_below_max` only at entry, while `withdraw` enforces the same gate on every non-liquidation exit. Because interest accrual keeps raising debt value after the borrow is admitted, an attacker who borrows up to just below the utilization ceiling can let accrual push the market's utilization above `params.max_utilization`. From that point every ordinary `withdraw` reverts with `UtilizationAboveMax`, freezing all supplier funds until someone repays debt. The attacker controls a solvent position and can keep it open indefinitely.

### Finding Description
`require_utilization_below_max` panics with `UtilizationAboveMax` when `borrowed * borrow_index` (ceiled) divided by `supplied * supply_index` (floored) exceeds `params.max_utilization`, for any market whose `max_utilization < RAY` [1](#0-0) . The pool's own README confirms this gate is applied to `borrow`, ordinary `withdraw`, and `claim_revenue`, while the gate is evaluated *after* `interest::global_sync` accrues debt in every mutation [2](#0-1) . The documented invariant admits the asymmetry: "Borrow debt minting, ordinary withdrawal and revenue claims reject utilization above the market ceiling... Accrual and bad-debt writeoff can exceed the ceiling; it is not a market-wide bound maintained by every operation" [3](#0-2) . Only liquidation withdrawals skip the gate, and suppliers cannot liquidate themselves [4](#0-3) . Accrual compounds debt via `accrue_step` chunks on every market touch, so utilization drifts upward autonomously once the borrow is placed [5](#0-4) .

Attack path, all unprivileged controller entrypoints:
1. `supply` collateral to attacker's account in spoke `S`.
2. `borrow` the target hub asset up to the largest amount that keeps post-accrual utilization just under `max_utilization` (also respecting `require_liquidation_buffer` [6](#0-5) ).
3. Wait (or repeatedly call `update_indexes`) until accrued interest pushes `borrowed_ceil / supplied_floor` over `max_utilization`.
4. Every victim `withdraw` on that market now reverts with `UtilizationAboveMax` (127); `claim_revenue` reverts too. The attacker keeps the position solvent by adding collateral, so no liquidation ever unwinds it.

### Impact Explanation
Temporary freezing of funds: all suppliers of the affected `(hub, token)` market are unable to withdraw any amount while utilization sits above the ceiling, and protocol revenue is unclaimable. The freeze lasts as long as the attacker chooses to service the debt — they can maintain it for an arbitrary duration — and ends only when enough debt is repaid (by the attacker or a third party) or the account is liquidated. In a market with thin alternative liquidity sources this strands the entire supplier base, matching the BASED incident class of an attacker freezing the pool.

### Likelihood Explanation
Requires a market configured with `max_utilization < 1.0` (a standard risk setting) and enough borrow capacity to reach the ceiling — the attacker must post collateral for the borrow, so cost is bounded by the collateral required plus interest. No privileged role, timing race, or oracle manipulation is needed; accrual does the work automatically. It is unlikely to be an accidental occurrence since borrows are admitted only below the ceiling, so realization requires deliberate positioning. Severity fits Medium: the freeze is temporary, recoverable by repayment, and requires the attacker to fund a large borrow.

### Recommendation
Apply the utilization gate asymmetrically: keep it on `borrow` and other debt-minting entries, but exempt `withdraw` (at minimum, exempt withdrawals up to available `cash`) and `claim_revenue`, or evaluate it only when the withdrawal itself would raise utilization. Alternatively, cap the measured utilization used for exits at the entry-time value, or add a small headroom (`max_utilization + exit_margin`) for exits so that passive accrual drift cannot strand suppliers.

### Proof of Concept
```text
// Market M: max_utilization = 0.95 RAY, cash deep enough that the
// liquidation buffer does not bind before utilization does.
1. attacker: controller.supply(account_id=0, spoke=S, [(COL, large)])
2. attacker: controller.borrow(id, [(M_asset, amt)])
   // amt chosen so post-accrual borrowed*index/supplied*index = 0.9499
   // borrow succeeds (gate checks at entry only)
3. time passes; every mutation calls interest::global_sync, growing
   borrow_index via accrue_step until utilization > 0.95
4. victim: controller.withdraw(victim_id, [(M_asset, x)])
   // global_sync runs, then require_utilization_below_max panics
   // with UtilizationAboveMax (127) -> all exits revert
5. attacker keeps HF > 1 by topping up collateral; freeze persists
   until debt is repaid or the account becomes liquidatable
```
The gate, its entry-only asymmetry, and the accrual-first ordering are confirmed in `contracts/pool/src/guards.rs:19-34`, `contracts/pool/src/interest.rs:20-33`, and `docs/reference/invariants.md` (INV-ACCT-08). Uncertainty: exact per-market `max_utilization` values in production config were not verified; if all markets run `max_utilization >= RAY`, the gate is skipped entirely and this does not apply.

### Citations

**File:** contracts/pool/src/guards.rs (L1-5)
```rust
//! Solvency, utilization and liquidity checks on the in-memory [`Cache`].
//!
//! Callers run them after interest accrual and before committing state.

use common::constants::{BPS, LIQUIDATION_BUFFER_BPS};
```

**File:** contracts/pool/src/guards.rs (L19-34)
```rust
pub(crate) fn require_utilization_below_max(env: &Env, cache: &Cache) {
    if cache.supplied() == Ray::ZERO || cache.params().max_utilization >= Ray::ONE {
        return;
    }

    let borrowed = cache.borrowed().mul_ceil(env, cache.borrow_index());
    if borrowed == Ray::ZERO {
        return;
    }
    let supplied = cache.supplied().mul_floor(env, cache.supply_index());
    assert_with_error!(
        env,
        supplied > Ray::ZERO && borrowed.div_ceil(env, supplied) <= cache.params().max_utilization,
        CollateralError::UtilizationAboveMax
    );
}
```

**File:** contracts/pool/src/guards.rs (L39-47)
```rust
pub(crate) fn require_liquidation_buffer(env: &Env, cache: &Cache, draw: i128) {
    let supplied = cache.unscale_supply_floor(cache.supplied());
    let reserved = mul_div_ceil(env, supplied, LIQUIDATION_BUFFER_BPS, BPS);
    assert_with_error!(
        env,
        cache.cash().saturating_sub(draw) >= reserved,
        CollateralError::InsufficientLiquidity
    );
}
```

**File:** docs/reference/invariants.md (L181-188)
```markdown
Borrow debt minting, ordinary withdrawal and revenue claims reject utilization
above the market ceiling. The gate divides ceiled debt value by floored supply
value and rounds the ratio up, so rounding cannot admit utilization above the
ceiling. It skips zero total supply, zero debt value and ceilings at least one
RAY. Debt against a zero floored supply value fails the gate.

Liquidation withdrawal skips the gate. Accrual and bad-debt writeoff can exceed
the ceiling; it is not a market-wide bound maintained by every operation.
```

**File:** contracts/pool/src/interest.rs (L20-33)
```rust
pub(crate) fn global_sync(env: &Env, cache: &mut Cache) {
    if !cache.needs_accrual() {
        return;
    }

    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
    }

    cache.mark_accrued();
}
```
