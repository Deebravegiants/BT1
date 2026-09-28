### Title
`recapitalize` pays out custody without funding, leaving the cash book overstated and supplier withdrawals frozen - (File: contracts/pool/src/ops/recapitalize.rs)

### Summary
`recapitalize` is an unprivileged pool entrypoint intended to let anyone top up a market after a bad-debt write-down without minting shares. The pool's liquidity guards (`require_reserves`, solvency checks) validate withdrawals against the internal cash book, not the SAC balance. Calling `recapitalize` drains token custody from the pool while the cash book still reports the funds as present, so suppliers' later withdrawals pass every pool guard and then revert inside the SAC transfer — funds are permanently frozen while the market reports itself solvent.

### Finding Description
The analog of the CVE's "wrong fallback logic" — state left inconsistent after a funding step fails to deliver — appears in `contracts/pool/src/ops/recapitalize.rs`. The regression test `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` in `contracts/pool/tests/flows.rs:3408-3483` demonstrates the exact sequence reachable by any address:

1. A supplier deposits normally; `cash` book equals token custody.
2. `client().recapitalize(&hub, &payer, &custody)` is called with the full pool balance as `amount`. The pool's token balance drops to `0`, yet `state_snapshot().cash` remains `>= deposit`.
3. The supplier's `withdraw(..., i128::MAX, ...)` passes `require_reserves` because the book claims liquidity exists, then fails inside the SAC `transfer` with the SAC's own `BalanceError = 10` — not the pool's `InsufficientLiquidity` or `PoolInsolvent` errors (asserted explicitly at lines 3454-3473).
4. Because the failure reverts, the book still overstates custody (line 3478-3482), so the freeze is permanent: every subsequent exit hits the same trap.

### Impact Explanation
Permanent freezing of user funds / protocol insolvency. Suppliers cannot withdraw because pool liquidity checks read the overstated book and the SAC transfer always fails; the market is functionally insolvent while reporting solvency, and no unprivileged path can repair the book-vs-custody gap since the failed exits roll back.

### Likelihood Explanation
`recapitalize` is in the in-scope unprivileged entrypoint set. A single caller supplies `payer` and `amount` up to the pool's full custody; the test exercises it with a freshly generated address and no privileges.

### Recommendation
Either require a measured inbound token transfer from `payer` equal to `amount` before touching custody (balance-delta measurement like `transfer_amount_measured` in `contracts/controller/src/payments.rs`), or reconcile the cash book downward when custody is disbursed so `require_reserves` sees the true balance. Add a post-op invariant that `cash <= token balance`.

### Proof of Concept
See `contracts/pool/tests/flows.rs:3408-3483`, which mints 10_000_000_000 to the pool, calls `recapitalize(hub, payer, custody)` from a generated address to drain custody to `0` while the book still reports the deposit, then shows `try_withdraw` failing with SAC `BalanceError = 10` rather than any pool liquidity guard — confirming the book overstates custody and the supplier can never exit. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/pool/tests/flows.rs (L3408-3440)
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

```

**File:** contracts/pool/tests/flows.rs (L3454-3483)
```rust
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
}
```

**File:** contracts/controller/src/payments.rs (L39-52)
```rust
/// Refunds only the controller balance increase since `balance_before`,
/// preserving the pre-existing balance; no-op for a nonpositive delta.
pub(crate) fn refund_controller_balance_delta(
    env: &Env,
    asset: &Address,
    balance_before: i128,
    refund_to: &Address,
) {
    let controller = env.current_contract_address();
    let excess = balance_delta_since(env, asset, &controller, balance_before);
    if excess > 0 {
        token::Client::new(env, asset).transfer(&controller, refund_to, &excess);
    }
}
```
