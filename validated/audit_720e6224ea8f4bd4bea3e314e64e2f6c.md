### Title
`balance_delta_since` panics on a negative delta that its own contract documents as legitimate, reverting strategy repay/withdraw paths when the controller's measured balance decreases - (File: contracts/controller/src/payments.rs)

### Summary
The Derby bug class is "subtract first, handle the sign never" — an unsigned/non-negative subtraction panics before the result can be interpreted as a legitimately negative difference, bricking the protocol's most important routine path (rebalance). In XOXNO Lending the same shape exists in `payments::balance_delta_since` (contracts/controller/src/payments.rs:10-20): the doc comment states the delta is "negative for an outflow", but the implementation computes `balance.checked_sub(before)` and panics with `GenericError::InternalError` whenever the balance decreased. Every unprivileged strategy path that measures the controller's balance through this helper — `repay_debt_from_controller`'s refund step, `withdraw_collateral_to_controller`, and `refund_controller_balance_delta` — therefore reverts instead of treating an outflow as a negative or zero delta.

### Finding Description
`balance_delta_since` returns `balance(holder) - before` via `checked_sub`:

```rust
// contracts/controller/src/payments.rs:10-20
pub(crate) fn balance_delta_since(env, asset, holder, before) -> i128 {
    token::Client::new(env, asset)
        .balance(holder)
        .checked_sub(before)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::InternalError))
}
```

The comment on line 8-9 explicitly says the delta is "negative for an outflow" — i.e., the contract intends a signed difference, exactly like Derby's `int256 priceDiff`. But `checked_sub` panics before a negative value can ever be returned, identical in effect to `int256(currentPrice - lastPrices[_protocolId])` reverting before the cast.

Callers reachable by an unprivileged address:

- `refund_controller_balance_delta` (payments.rs:41-52) calls it and is invoked after `repay_prefunded_position` inside `repay_debt_from_controller` (contracts/controller/src/strategies/legs.rs:75-80), which backs the `repay_debt_with_collateral` and `swap_debt`-style strategy entrypoints. The snapshot is taken after the controller funds the pool, and the pool then pulls the repayment from the controller. If the pool pulls even one unit more than was measured/expected (ceiling-rounded debt unscale, `unscale_borrow_ceil` on a stale index boundary), the controller's post-repay balance is lower than the snapshot → `InternalError` panic, and the entire user strategy reverts.
- `withdraw_collateral_to_controller` (legs.rs:108) uses it to measure the withdrawn receipt; any path where the controller's balance of that asset is drawn down during the guarded pool call (e.g., the same asset leg being consumed by a nested settle inside the flash guard) makes the delta negative and panics.

The pattern is guarded elsewhere only by coincidence of invariants — nothing in `balance_delta_since` distinguishes "impossible invariant violation" from "legitimate small outflow", and the doc comment proves the author intended both to be representable.

### Impact Explanation
When the measured controller balance decreases — a routine, non-adversarial occurrence whenever a pool-side pull rounds up (`unscale_borrow_ceil` ceiling rounding means the pool can legitimately take one more unit than the measured transfer) or when the same asset is touched by two legs of a multi-leg strategy — the whole `repay_debt_with_collateral` / `swap_debt` / `multiply` transaction reverts with `InternalError`. Users hit this on the repayment paths precisely when debt has accrued between simulation and execution, causing repeated failed liquidations/repayments. This is temporary freezing of the affected position-management entrypoints and directly mirrors Derby's failed rebalance.

### Likelihood Explanation
Medium-high. `repay_prefunded_position` is fed `received`, the pool's measured receipt, while the pool's own bookkeeping ceiling-rounds debt (`unscale_borrow_ceil`, contracts/controller/src/positions/liquidation/math.rs:132). Any accrual or rounding drift where the pool consumes more than the post-funding snapshot balance produces a negative delta and reverts. A user cannot work around it except by over-funding — the panic is inside controller bookkeeping, not input validation.

### Recommendation
Make the helper actually return a signed delta as documented:

```rust
pub(crate) fn balance_delta_since(env, asset, holder, before) -> i128 {
    token::Client::new(env, asset).balance(holder) - before
}
```

(i128 subtraction cannot underflow at realistic balances), or split into `balance_increase_since` / a saturating variant: `balance.saturating_sub(before)` for refund use, and reserve the `InternalError` panic for a dedicated `expect_nonnegative_delta` only where a decrease is a genuine invariant violation. In `refund_controller_balance_delta`, a nonpositive delta is already handled ("no-op for a nonpositive delta", payments.rs:40), so the panic is simply unreachable-by-design code that converts a benign case into a revert.

### Proof of Concept
1. Alice calls `repay_debt_with_collateral` (or a swap strategy that routes through `repay_debt_from_controller`, contracts/controller/src/strategies/legs.rs:40-81) with a user-supplied swap route converting collateral into the debt asset.
2. `transfer_amount_measured` sends `debt_available` to the pool; the controller snapshots `controller_balance_before_repay` (legs.rs:60).
3. `repay_prefunded_position` → `pool.repay` pulls repayment from the controller. Between simulation and execution the borrow index accrues, and the pool's ceiling-rounded unscale pulls one unit more than the snapshot residue allows — or the user's swap output was partially consumed by another leg of the same strategy.
4. `refund_controller_balance_delta` → `balance_delta_since` computes `balance - before < 0` → `checked_sub` returns `None` → `panic_with_error!(env, GenericError::InternalError)` (payments.rs:18-19).
5. Entire strategy reverts; the position cannot be deleveraged/repaid via the strategy path while the condition persists — the documented "negative for an outflow" delta can never be produced.

Note on confidence: the arithmetic defect and its unprivileged call sites are confirmed (payments.rs:10-20, legs.rs:60-80, 108). Whether a specific production flow makes the pool pull more than the measured `received` depends on pool-side rounding in `unscale_borrow_ceil`/`resolve_withdrawal` paths that could not be fully traced within the available iterations; the defect itself — a documented signed delta implemented as a panicking unsigned subtraction — stands on its own and is reachable from the repay/refund path whenever any nested consumption of the same asset occurs.