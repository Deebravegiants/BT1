### Title
`get_liquidation_estimate` omits execution-time checks, returning successful estimates for liquidations that always revert — (File: contracts/controller/src/views.rs)

### Summary
Analogous to `BunniQuoter` skipping hooklet calls, the controller's quoting view `get_liquidation_estimate` reuses `build_liquidation_plan` but skips every check that `process_liquidation` layers on top of the plan — credit-receiver validation, non-empty payment requirements, receiver position-limit enforcement, and measured-receipt rescaling. The estimate therefore reports profitable seizures for calls that the real `liquidate` entrypoint always reverts.

### Finding Description
The estimate path in `liquidation_estimations_detailed` performs only `require_view_inputs_bound` (a length cap) and then calls `build_liquidation_plan` directly. [1](#0-0) 

`process_liquidation` calls the same planner but wraps it with additional gates the view never runs:

- `resolve_seize_receiver` runs before planning and enforces `requested != account_id` (`SelfLiquidationNotAllowed`), receiver existence, owner-or-delegate authorization, `SpokeMismatch`, and `AccountModeMismatch` (receiver must be `Normal` mode). [2](#0-1) [3](#0-2) 
- `require_non_empty_payments` is enforced both on the input and on the plan's `repaid` output; the estimate never checks either, so an all-released or empty payment plan is reported as valid. [4](#0-3) 
- `require_credit_position_limit` caps the receiver's credited shares; the view reports share amounts that execution would refuse to credit. [5](#0-4) 
- `scale_seizures_to_received` rescales seizure to measured token receipts; the estimate reports the unscaled plan amounts. [6](#0-5) 

### Impact Explanation
Any unprivileged liquidator or bot that sizes a `liquidate` call from `get_liquidation_estimate` (the documented workflow: "Simulate `get_liquidation_estimate` with the exact same payments and mode immediately before building the write") receives a successful, profitable-looking estimate — including a RAY-share breakdown for a `Credit` receiver — for transactions that deterministically revert. At minimum this burns submission fees; at protocol level, liquidation flows built and tested against the view can systematically fail on unhealthy accounts, leaving undercollateralized positions open longer and increasing bad-debt accrual on the pool.

### Likelihood Explanation
The divergence is unconditional: every `SeizeMode::Credit(id)` estimate where `id` is the liquidated account, a different-spoke account, a non-`Normal` account, an unauthorized account, or a nonexistent account returns success while `liquidate` reverts. The same holds for `Credit(id)` receivers already at the position limit, and for payment vectors whose plan normalizes to empty repayment. These inputs are fully reachable by an unprivileged caller through the public `get_liquidation_estimate` view.

### Recommendation
Mirror the execution preconditions in `liquidation_estimations_detailed`: run `require_non_empty_payments` on the input, resolve and validate the credit receiver (existence, spoke, mode, authorization, not the liquidated account, position-limit headroom) read-only, and re-check `result.repaid` non-emptiness before returning the estimate, so the view only reports plans that `liquidate` could actually settle.

### Proof of Concept
1. Create a debt position for account `A` and move prices so `health_factor(A) < WAD`.
2. Call `get_liquidation_estimate(A, debt_payments, SeizeMode::Credit(A))` — the view returns a normal `LiquidationEstimate` with seized shares and fees, because `resolve_seize_receiver` is never invoked on the view path.
3. Submit `liquidate(liquidator, A, debt_payments, SeizeMode::Credit(A))` — execution reverts with `CollateralError::SelfLiquidationNotAllowed` at `resolve_seize_receiver`. [7](#0-6) 
4. Variant: use `SeizeMode::Credit(B)` where `B` is in a different spoke or `Isolated` mode — the estimate succeeds, execution reverts with `SpokeMismatch`/`AccountModeMismatch`. [8](#0-7)

### Citations

**File:** contracts/controller/src/views.rs (L199-209)
```rust
pub(crate) fn liquidation_estimations_detailed(
    env: &Env,
    account_id: u64,
    debt_payments: &Vec<HubPayment>,
    seize_mode: SeizeMode,
) -> LiquidationEstimate {
    require_view_inputs_bound(env, debt_payments);
    let mut cache = Context::new_view(env);
    let account = storage::get_account(env, account_id);

    let result = build_liquidation_plan(env, &account, debt_payments, &mut cache).into_result();
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L50-66)
```rust
    require_non_empty_payments(env, debt_payments);

    // Reject an unusable receiver before moving tokens.
    let mut receiver = resolve_seize_receiver(
        env, liquidator, account_id, &account, seize_mode, &mut cache,
    );

    // Share payment normalization and positivity checks with the estimate view.
    let liquidation_plan = plan::build_liquidation_plan(env, &account, debt_payments, &mut cache);
    let offered = liquidation_plan
        .repayment
        .full_close
        .then(|| payments::aggregate_positive_payments(env, debt_payments));

    let result = liquidation_plan.into_result();

    require_non_empty_payments(env, &result.repaid);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L78-79)
```rust
    let repay_usd = math::sum_repaid_usd(env, &result.repaid);
    let seized = math::scale_seizures_to_received(env, &result.seized, received_usd, repay_usd);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L84-93)
```rust
        Some((_, receiving_account)) => {
            apply::require_credit_position_limit(env, receiving_account, &seized, &mut cache);
            apply::apply_liquidation_share_credit(
                env,
                &mut account,
                receiving_account,
                &seized,
                &mut cache,
            );
        }
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L172-192)
```rust
    // Crediting the same account would undo the seizure.
    assert_with_error!(
        env,
        requested != account_id,
        CollateralError::SelfLiquidationNotAllowed
    );

    let receiver = storage::get_account(env, requested);
    account::require_owner_or_delegate(env, requested, liquidator, &receiver.owner);
    assert_with_error!(
        env,
        receiver.spoke_id == account.spoke_id,
        SpokeError::SpokeMismatch
    );
    assert_with_error!(
        env,
        receiver.mode == PositionMode::Normal,
        GenericError::AccountModeMismatch
    );

    Some((requested, receiver))
```
