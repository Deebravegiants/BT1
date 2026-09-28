### Pool recapitalization refunds unfunded deposits and drains user liquidity - (`contracts/pool/src/ops/recapitalize.rs`)

### Summary

`recapitalize` trusts the caller-declared `amount`, books only the current backing shortfall, and then unconditionally transfers the unapplied `refund` back to `payer`. The function never measures whether the pool actually received `amount`. If the preceding controller transfer fails to deliver the full declared amount, the refund is paid out of pre-existing pool custody, while the cash ledger only records `applied`.

### Finding Description

The vulnerable flow is:

1. `accounting` accepts nonnegative `amount`.
2. It calculates `applied = amount.min(guards::backing_shortfall(&cache))`.
3. It calculates `refund = amount - applied`.
4. It credits only `applied` to the pool's cash book and commits that state.
5. `apply` then transfers `refund` to `payer`.

This is implemented without a token-balance check between receiving the recapitalization and paying the refund:

```rust
let applied = amount.min(guards::backing_shortfall(&cache));
let refund = amount
    .checked_sub(applied)
    .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

cache.credit_cash(applied);
cache.commit();
```

from `contracts/pool/src/ops/recapitalize.rs:52-58`, followed by:

```rust
outcome.cache.transfer_out(&payer, outcome.refund);
```

from `contracts/pool/src/ops/recapitalize.rs:34`. [1](#0-0) [2](#0-1) 

The pool interface documents the intended precondition that the controller transfers `amount` before the call, but the pool does not verify that the transfer actually delivered `amount`. [3](#0-2) 

The repository already contains a regression-style test showing this exact consequence: a declared recapitalization refund can remove the pool's entire token custody while leaving `cash` unchanged. [4](#0-3)  The test then demonstrates that a supplier withdrawal is approved by the pool's accounting guard but fails inside the SAC token transfer because custody is gone. [5](#0-4) 

### Impact Explanation

This is theft of pool funds and temporary freezing of supplier withdrawals.

The payer can receive an amount it never deposited whenever `refund > 0`. Because only `applied` is credited to `cash`, the pool's accounting continues to claim that the refunded liquidity is available. Subsequent withdrawals pass `Cache::require_reserves`, then fail at the token transfer because the physical balance has already been drained. [6](#0-5) [7](#0-6) 

If the controller sends the full declared amount with a compliant token, the impact is limited to returning the true excess. The unsafe behavior appears when actual receipt differs from `amount`, such as a failed or short transfer caused by token behavior or an inconsistent controller-side funding leg. The tested state transition itself shows the accounting invariant can be broken: token custody becomes zero while `cash` still claims the funds are present. [8](#0-7) 

### Likelihood Explanation

Likelihood depends on whether every production `Controller::recapitalize` call is guaranteed to deliver exactly `amount` before invoking `LiquidityPool::recapitalize`.

The endpoint is reachable through the unprivileged `recapitalize` path listed in scope, but `LiquidityPool::recapitalize` itself is owner-only and expects the controller to pre-fund it. [3](#0-2)  I did not have a remaining tool iteration to verify the controller's recapitalize funding implementation, so the practical exploit path cannot be fully confirmed here.

The missing receipt check is nevertheless real in in-scope production code: the pool treats a parameter as already received money and pays a refund against prior custody rather than measuring `balance(pool) - balance_before`. The checked-in test proves the resulting pool-state divergence is possible once the precondition fails. [9](#0-8) 

### Recommendation

Measure recapitalization receipts instead of trusting the argument:

- Record `token.balance(pool)` before the funding transfer, or require the controller to use an explicit settlement protocol.
- Compute `received = balance_after_funding - balance_before`.
- Require `received == amount` before committing cash or paying a refund.
- Alternatively, treat the measured `received` as the deposit: `applied = received.min(shortfall)` and `refund = received - applied`.
- Ensure that `refund` can never exceed the newly received amount, not merely `amount - applied`.

A balance-delta pattern is already used elsewhere in the controller payment code: `balance_delta_since` explicitly exists to account for measured receipts rather than reported transfer amounts. [10](#0-9) 

### Proof of Concept

Conceptual sequence:

1. Seed a market with supplier-backed custody `D` and corresponding `cash >= D`.
2. Invoke recapitalization accounting with `amount = D` while the pool receives `0`.
3. Suppose the market has no backing shortfall. Then:
   - `applied = 0`
   - `refund = D`
   - `cash` remains unchanged
   - `transfer_out(payer, D)` transfers all existing custody to `payer`
4. A supplier calls `withdraw`.
5. The withdrawal passes the pool's cash-reserve accounting because `cash` still includes `D`.
6. The SAC token transfer fails because the pool balance is `0`.

The repository's test performs this same sequence and asserts the incorrect outcome:

```rust
let custody = token.balance(&t.pool);
t.client().recapitalize(&hub(&t.asset), &payer, &custody);
assert_eq!(token.balance(&t.pool), 0, "custody is gone");

let book = t.state_snapshot().cash;
assert!(
    book >= deposit,
    "the book still claims more than the supplier's deposit: {book}"
);
```

from `contracts/pool/tests/flows.rs:3430-3439`, followed by a withdrawal that fails only inside the token transfer. [11](#0-10)

### Citations

**File:** contracts/pool/src/ops/recapitalize.rs (L26-35)
```rust
pub(crate) fn apply(
    env: &Env,
    hub_asset: HubAssetKey,
    payer: Address,
    amount: i128,
) -> PoolAmountMutation {
    let outcome = accounting(env, hub_asset, amount);

    outcome.cache.transfer_out(&payer, outcome.refund);

```

**File:** contracts/pool/src/ops/recapitalize.rs (L52-58)
```rust
    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();
```

**File:** contracts/pool/src/lib.rs (L182-194)
```rust
    /// Credits cash up to the market's backing shortfall
    /// (`guards::backing_shortfall`) and transfers the excess back to `payer`.
    /// The controller transfers `amount` in before this call. Restricted to
    /// the owner; returns a [`PoolAmountMutation`] with the amount applied.
    #[only_owner]
    fn recapitalize(
        env: Env,
        hub_asset: HubAssetKey,
        payer: Address,
        amount: i128,
    ) -> PoolAmountMutation {
        ops::recapitalize::apply(&env, hub_asset, payer, amount)
    }
```

**File:** contracts/pool/tests/flows.rs (L3376-3401)
```rust
/// Shared tail of the unfunded-refund tests: the declared amount came back to
/// the payer, custody is gone, and the cash book did not move.
fn assert_unfunded_refund_drained_custody(
    t: &TestSetup,
    payer: &Address,
    declared: i128,
    before: &PoolStateRaw,
) {
    let token = token::Client::new(&t.env, &t.asset);
    let after = t.state_snapshot();
    assert_eq!(
        token.balance(payer),
        declared,
        "the payer is refunded in full for a payment that never happened"
    );
    assert_eq!(
        token.balance(&t.pool),
        0,
        "the pool's entire custody has left the contract"
    );
    assert_eq!(
        after.cash, before.cash,
        "the cash book is untouched, so the pool still reports the paid-out \
         funds as present"
    );
    assert_pool_state_eq(&after, before);
```

**File:** contracts/pool/tests/flows.rs (L3404-3406)
```rust
/// After an unfunded refund, `cash` overstates custody. `Cache::require_reserves`
/// reads the book, not the balance, so it admits exits that then fail inside
/// the SAC transfer. The market reports itself solvent and cannot pay.
```

**File:** contracts/pool/tests/flows.rs (L3408-3482)
```rust
fn test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody() {
    let t = TestSetup::new();
    let token = token::Client::new(&t.env, &t.asset);
    let token_admin = token::StellarAssetClient::new(&t.env, &t.asset);
    let payer = Address::generate(&t.env);
    let receiver = Address::generate(&t.env);

    // A legitimate supplier, with custody moved in as the controller would.
    let deposit = 10_000_000_000i128;
    token_admin.mint(&t.pool, &deposit);
    let supplied = t
        .client()
        .supply(&t.sup(0, deposit))
        .get_unchecked(0)
        .position
        .scaled_amount;
    assert_eq!(
        t.state_snapshot().cash,
        token.balance(&t.pool),
        "fixture guard: book and custody must still agree after the deposit"
    );

    // Drain every token via an unfunded refund.
    let custody = token.balance(&t.pool);
    t.client().recapitalize(&hub(&t.asset), &payer, &custody);
    assert_eq!(token.balance(&t.pool), 0, "custody is gone");

    let book = t.state_snapshot().cash;
    assert!(
        book >= deposit,
        "the book still claims more than the supplier's deposit: {book}"
    );

    // The supplier's exit clears the pool's own liquidity guard -- the book
    // says the cash is there -- and then fails in the token transfer.
    let outcome = t
        .client()
        .try_withdraw(&receiver, &false, &t.wdr(supplied, i128::MAX, 0));
    assert!(
        outcome.is_err(),
        "the withdraw cannot be paid, so it must fail"
    );
    // The failure must come from custody, not from a pool guard. The SAC
    // reports insufficient balance as its own contract error `BalanceError = 10`.
    // The asserts check that exact code and that neither pool liquidity guard
    // fired: `require_reserves` read the book and let the exit through.
    const SAC_BALANCE_ERROR: u32 = 10;
    match outcome {
        Err(Ok(err)) => {
            assert_ne!(
                err,
                Error::from_contract_error(CollateralError::InsufficientLiquidity as u32),
                "the pool's own liquidity guard must NOT be what stopped this -- \
                 it reads the cash book, which still shows the funds"
            );
            assert_ne!(
                err,
                Error::from_contract_error(CollateralError::PoolInsolvent as u32),
                "the pool's solvency guard must NOT be what stopped this either"
            );
            assert_eq!(
                err,
                Error::from_contract_error(SAC_BALANCE_ERROR),
                "the exit must fail inside the SAC transfer for want of custody"
            );
        }
        Err(Err(host_abort)) => panic!("expected a SAC contract error, got {host_abort:?}"),
        Ok(_) => unreachable!("asserted is_err above"),
    }
    assert_eq!(token.balance(&receiver), 0, "the supplier received nothing");
    assert_eq!(
        t.state_snapshot().cash,
        book,
        "the failed exit rolled back, so the book still overstates custody"
    );
```

**File:** contracts/controller/src/payments.rs (L8-20)
```rust
/// Returns the measured balance change since `before`, negative for an outflow.
/// Custody accounting uses this delta rather than reported transfer amounts.
pub(crate) fn balance_delta_since(
    env: &Env,
    asset: &Address,
    holder: &Address,
    before: i128,
) -> i128 {
    token::Client::new(env, asset)
        .balance(holder)
        .checked_sub(before)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::InternalError))
}
```
