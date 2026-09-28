### Title
Pending bad-debt write-down is not applied at withdrawal time, letting suppliers exit at the pre-loss index and concentrate the loss on remaining suppliers — (File: contracts/controller/src/positions/liquidation/mod.rs)

### Summary
The XOXNO Lending analog of CVE-2022-23035's "cleanup deferred then skipped while stale state is assumed valid" is the protocol's lazy bad-debt socialization. Debt write-down (the analog of the deferred IRQ cleanup) is only applied inside `liquidate`/`clean_bad_debt` via `execute_bad_debt_cleanup` → `apply_bad_debt_to_supply_index`. Between the moment an account becomes insolvent and the moment anyone triggers the cleanup, `withdraw`/`withdraw_all` continues to pay suppliers out at the stale, un-written-down `supply_index`, and the pool gate (`backing_shortfall` face-value accounting / `require_reserves`) does not reserve the pending loss. A supplier who exits first receives full value; the deferred write-down then lands entirely on the suppliers who stayed.

### Finding Description
Once a borrower's collateral crashes, the account is insolvent but no supply-index write-down has occurred: `socialize_bad_debt` / `check_bad_debt_after_liquidation` only run inside a liquidation or `clean_bad_debt` call [1](#0-0) . Withdrawal persists positions and gates only on cash reserves, not on pending bad debt [2](#0-1) . The pinned test `supplier_can_exit_ahead_of_bad_debt_writedown` demonstrates the exact mechanism: Bob withdraws everything at the un-written-down index, then the liquidation applies the write-down, and Carol's loss is ~4x larger than if Bob had stayed [3](#0-2) . Like the Xen bug, the "retry" (write-down) is deferred, other code paths keep assuming the stale pointer/index is valid, and when cleanup finally runs the freed value has already been extracted.

### Impact Explanation
Protocol insolvency borne unequally by users: large or fast suppliers (or an attacker who supplies, waits for an insolvency event, exits, then triggers `liquidate`/`clean_bad_debt` themselves — all unprivileged entrypoints) recover 100% while passive suppliers absorb an amplified write-down. In a thin market this can leave the last suppliers with claims exceeding remaining cash — permanent loss of user funds. Reachable entirely through `withdraw` and `liquidate`/`clean_bad_debt` by a single unprivileged address.

### Likelihood Explanation
Requires a real insolvency event (price crash or stale-price-driven bad debt) plus a market shallow enough that one supplier's exit meaningfully shifts the loss. Any participant can race the write-down; the incentive exists whenever bad debt is pending, since exiting is strictly dominant. The dust-capped permissionless `clean_bad_debt` and forced socialization gates do not close the window for larger residual collateral, since liquidation itself applies the write-down at execution time.

### Recommendation
Charge withdrawals against a pro-forma write-down: when `require_reserves`/`backing_shortfall` detects pending unrecoverable debt (e.g., any account whose risk totals satisfy `is_socializable_bad_debt`, or a tracked pending-loss accumulator updated at price/index refresh in `update_indexes`), either block withdrawal of the affected market or reduce the effective `supply_index` used to pay out so the loss is socialized at exit time rather than at cleanup time. Alternatively, apply `apply_bad_debt_to_supply_index` eagerly during index accrual for accounts already known insolvent.

### Proof of Concept
Reproduced verbatim by the in-repo test `supplier_can_exit_ahead_of_bad_debt_writedown` [4](#0-3) :

1. Bob supplies 75 ETH, Carol 25 ETH; Alice supplies 10 USDC and borrows 0.003 ETH.
2. Crash USDC to $0.10 (`set_price`) — Alice is now insolvent; no write-down has run.
3. Bob calls `withdraw`/`withdraw_all` on ETH — paid in full at the stale `supply_index` (passes `require_reserves` because Alice's debt still counts at face).
4. Anyone calls `liquidate(LIQUIDATOR, ALICE, "ETH", …)` — `check_bad_debt_after_liquidation` → `execute_bad_debt_cleanup` → `apply_bad_debt_to_supply_index` writes the loss down.
5. Carol's loss after Bob's dodge is ~4x her passive loss (asserted `amplification > 3.0`); in a two-supplier market Carol alone would absorb the entire write-down while Bob escaped whole.

### Citations

**File:** contracts/controller/src/positions/liquidation/mod.rs (L212-238)
```rust
fn socialize_bad_debt(env: &Env, account_id: u64, gate: BadDebtGate) {
    let mut cache = Context::new(env);
    let account = storage::get_account(env, account_id);

    assert_with_error!(
        env,
        !account.borrow_positions.is_empty(),
        CollateralError::DebtPositionNotFound
    );

    let totals = risk::calculate_account_risk_totals(
        env,
        &mut cache,
        &account.supply_positions,
        &account.borrow_positions,
    );

    let admits = match gate {
        BadDebtGate::DustCapped => {
            is_socializable_bad_debt(totals.total_debt, totals.total_collateral)
        }
        BadDebtGate::InsolventOnly => totals.total_debt > totals.total_collateral,
    };
    assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt);

    bad_debt::execute_bad_debt_cleanup(env, &mut cache, account_id, &account, &totals);
}
```

**File:** contracts/controller/src/positions/mod.rs (L153-170)
```rust
pub(crate) fn persist_account_positions(
    env: &Env,
    account_id: u64,
    account: &Account,
    sides: PositionSides,
    remove_if_empty: bool,
) {
    if sides != PositionSides::Debt {
        storage::set_supply_positions(env, account_id, &account.supply_positions);
    }
    if sides != PositionSides::Supply {
        storage::set_debt_positions(env, account_id, &account.borrow_positions);
    }
    storage::renew_user_account(env, account_id);
    if remove_if_empty {
        account::cleanup_account_if_empty(env, account, account_id);
    }
}
```

**File:** tests/test-harness/tests/controller/bad_debt_index.rs (L401-473)
```rust
#[test]
fn supplier_can_exit_ahead_of_bad_debt_writedown() {
    // Scenario A: nobody dodges. Bob 75%, Carol 25% of the ETH supply.
    let mut a = setup();
    a.supply(BOB, "ETH", 75.0);
    a.supply(CAROL, "ETH", 25.0);
    a.supply(ALICE, "USDC", 10.0);
    a.borrow(ALICE, "ETH", 0.003);

    let carol_before_a = a.supply_balance(CAROL, "ETH");
    a.set_price("USDC", usd_cents(10));
    a.liquidate(LIQUIDATOR, ALICE, "ETH", 0.001);
    let carol_loss_a = carol_before_a - a.supply_balance(CAROL, "ETH");

    // Scenario B: identical state, but Bob withdraws before the write-down.
    let mut b = setup();
    b.supply(BOB, "ETH", 75.0);
    b.supply(CAROL, "ETH", 25.0);
    b.supply(ALICE, "USDC", 10.0);
    b.borrow(ALICE, "ETH", 0.003);

    let carol_before_b = b.supply_balance(CAROL, "ETH");
    let bob_before_b = b.supply_balance(BOB, "ETH");
    let bob_wallet_before = b.token_balance(BOB, "ETH");

    // The crash is public state. Alice is insolvent from here on, but no
    // write-down has been applied yet.
    b.set_price("USDC", usd_cents(10));
    b.assert_liquidatable(ALICE);

    // Bob exits at the un-written-down index. No gate stops him: the
    // liquidation buffer only guards borrow draws, and `backing_shortfall`
    // still values Alice's uncollateralised debt at face.
    b.withdraw_all(BOB, "ETH");
    let bob_recovered = b.token_balance(BOB, "ETH") - bob_wallet_before;

    b.liquidate(LIQUIDATOR, ALICE, "ETH", 0.001);
    let carol_loss_b = carol_before_b - b.supply_balance(CAROL, "ETH");

    assert!(
        bob_recovered >= bob_before_b,
        "Bob exits whole: supplied={:.9} recovered={:.9}",
        bob_before_b,
        bob_recovered
    );
    assert!(
        carol_loss_b > carol_loss_a,
        "dodging must push loss onto Carol: A={:.9} B={:.9}",
        carol_loss_a,
        carol_loss_b
    );

    // Carol holds 25% of supply, so passing the whole loss to her is ~4x.
    let amplification = carol_loss_b / carol_loss_a;
    assert!(
        amplification > 3.0,
        "expected ~4x concentration onto the remaining supplier, got {:.3}x \
         (A={:.9} B={:.9})",
        amplification,
        carol_loss_a,
        carol_loss_b
    );

    std::println!(
        "A4-econ dodge: bob_supplied={:.9} bob_recovered={:.9} \
         carol_loss_passive={:.9} carol_loss_after_dodge={:.9} amplification={:.3}x",
        bob_before_b,
        bob_recovered,
        carol_loss_a,
        carol_loss_b,
        amplification
    );
}
```
