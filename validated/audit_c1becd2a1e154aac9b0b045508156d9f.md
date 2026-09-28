### Title
Suppliers can atomically exit before `clean_bad_debt` and shift the entire write-down to remaining suppliers - (File: contracts/pool/src/ops/withdraw.rs)

### Summary
An unprivileged supplier can withdraw at the pre-socialization supply index, call `clean_bad_debt` on an eligible insolvent account, and immediately re-enter the now-written-down market. Because the withdrawal happens before the debt is socialized, the attacker escapes the loss while the remaining suppliers absorb a disproportionately large supply-index reduction.

### Finding Description
`withdraw` burns supply shares and pays the current claim after only checking reserves, maximum utilization, and the “no debt without supply” invariant. It does not account for known-but-unexecuted bad debt before releasing funds. [1](#0-0) 

The permissionless `clean_bad_debt` path only requires caller authentication, no active flash loan, outstanding debt, `total_debt > total_collateral`, and collateral at or below the fixed dust threshold. [2](#0-1) [3](#0-2) [4](#0-3) 

Cleanup sends the account’s debt positions to `pool_seize_positions_call`, which converts each unpaid debt leg into a market-wide supply-index write-down. [5](#0-4) [6](#0-5) 

A supplier that has already withdrawn has no shares in the market when `apply_bad_debt_to_supply_index` runs, so the entire loss is concentrated into the suppliers that remain. The test `exit_then_clean_then_re_enter_dodges_the_write_down_when_utilization_allows` demonstrates this exact sequence atomically: withdraw, call `CleanBadDebt`, and supply again. [7](#0-6) 

### Impact Explanation
This is theft of user funds through loss reallocation: the attacker exits at the pre-write-down index, while passive suppliers absorb the bad debt that would otherwise have been shared pro rata.

The repository’s regression test shows a 75% supplier withdrawing before cleanup and increasing the remaining 25% supplier’s loss by more than three times. [8](#0-7) [9](#0-8) 

The attacker can then re-enter after the write-down because `supply` mints shares at the reduced index once the market is backed again. [10](#0-9) 

### Likelihood Explanation
The attacker only needs an existing supply position, enough pool cash and utilization headroom to withdraw, and a public dust-insolvent account eligible for `clean_bad_debt`.

All required operations are callable by an unprivileged address: `withdraw` for its own account, `clean_bad_debt` for any eligible account, and `supply` to create a fresh account. [11](#0-10) 

The sequence can be performed atomically by a contract-controlled caller, eliminating the need to win a separate transaction race. [12](#0-11) 

The primary constraint is liquidity: a withdrawal can fail the reserve, utilization, or last-supplier guard before cleanup. [1](#0-0) 

### Recommendation
Track mark-to-market bad debt as a pending market liability and apply it before ordinary withdrawals release cash.

At minimum, calculate the withdrawal haircut from current collateral/debt prices or maintain a pool-level pending-bad-debt reserve updated by liquidation eligibility checks. Alternatively, add a permissionless market checkpoint that identifies and socializes eligible bad debt before allowing a withdrawal that would reduce the remaining supply base.

### Proof of Concept
Assume:

1. Attacker holds 50 ETH of supply shares.
2. Bob holds the remaining ETH supply shares.
3. Victim has ETH debt and collateral worth at most `$5`, with `total_debt > total_collateral`.

The attacker executes the following sequence atomically:

1. `withdraw(caller = attacker, account_id = attacker_account, withdrawals = [(ETH, 0)], to = attacker)` to receive the full ETH claim at the pre-write-down supply index.
2. `clean_bad_debt(caller = attacker, account_id = victim)`, which burns the victim’s debt shares and lowers the ETH supply index for Bob’s remaining shares.
3. `supply(caller = attacker, account_id = 0, spoke_id = attacker_spoke, assets = [(ETH, 50 ETH)])` to re-enter the written-down market.

The existing composition test performs exactly this sequence and proves that the attacker retains its stake while Bob absorbs the write-down. [13](#0-12)

### Citations

**File:** contracts/pool/src/ops/withdraw.rs (L111-118)
```rust
fn gate_and_debit(env: &Env, cache: &mut Cache, net_transfer: i128, skip_utilization_check: bool) {
    cache.require_reserves(net_transfer);

    if !skip_utilization_check {
        guards::require_utilization_below_max(env, cache);
    }
    guards::require_supply_for_debt(env, cache);
    cache.debit_cash(net_transfer);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-199)
```rust
/// Authorizes permissionless dust-gated cleanup outside flash loans.
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L222-235)
```rust
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
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L23-27)
```rust
/// Admits socialization when debt exceeds collateral and collateral is at or
/// below `BAD_DEBT_USD_THRESHOLD` (WAD USD).
pub(crate) fn is_socializable_bad_debt(total_debt: Wad, total_collateral: Wad) -> bool {
    total_debt > total_collateral && total_collateral <= Wad::from(BAD_DEBT_USD_THRESHOLD)
}
```

**File:** contracts/controller/src/positions/liquidation/bad_debt.rs (L35-49)
```rust
    for (hub_asset, position) in iter_debt_positions(&account.borrow_positions) {
        cache.apply_spoke_exit(
            account.spoke_id,
            UsageSide::Borrow,
            &hub_asset,
            position.scaled_amount,
        );
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Borrow,
            position: (&position).into(),
        });
    }
    let pool_addr = cache.cached_pool_address();
    pool_seize_positions_call(env, &pool_addr, &entries);
```

**File:** contracts/pool/src/ops/seize.rs (L23-28)
```rust
    match entry.side {
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
        }
```

**File:** tests/test-harness/tests/composition/supplier_exit_before_socialization_is_bounded_by_utilization.rs (L52-78)
```rust
#[test]
fn exit_then_clean_then_re_enter_dodges_the_write_down_when_utilization_allows() {
    let Seed {
        t,
        runner,
        runner_account,
        victim,
    } = seed(true, 0.0);
    let bob_before = t.supply_balance_raw(BOB, "ETH");
    let ops: Vec<Op> = vec![
        &t.env,
        withdraw_op(&t, runner_account, "ETH", 0, None),
        Op::CleanBadDebt(AccountOp { account_id: victim }),
        supply_op(&t, 0, "ETH", 50 * U),
    ];
    let new_id = t
        .run_script(&runner, &ops)
        .expect("atomic exit, clean, re-enter");
    assert!(new_id > 0 && new_id != runner_account);
    assert!(
        t.supply_balance_raw_for(new_id, "ETH") >= 50 * U - 1,
        "the runner kept its whole stake"
    );
    assert!(
        t.supply_balance_raw(BOB, "ETH") < bob_before,
        "BOB absorbed the entire write-down"
    );
```

**File:** tests/test-harness/tests/controller/bad_debt_index.rs (L396-438)
```rust
/// Bad debt is written down only when a liquidation or cleanup call runs, and
/// `backing_shortfall` counts the unrecoverable debt at face value until then.
/// A supplier can exit at the pre-write-down index and leave the loss on the
/// suppliers who stay. Runs the same crash with Bob passive and with Bob
/// exiting first, and compares Carol's loss.
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
```

**File:** tests/test-harness/tests/controller/bad_debt_index.rs (L440-458)
```rust
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
```

**File:** contracts/pool/src/ops/supply.rs (L23-40)
```rust
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    guards::require_backed_market(env, &cache);

    let minted = cache.calculate_scaled_supply(amount);
    assert_with_error!(
        env,
        amount == 0 || minted.raw() > 0,
        GenericError::SupplyRoundsToZeroShares
    );

    position = position.checked_add(env, minted);
    cache.mint_supply(minted);

    cache.credit_cash(amount);

    let snapshot = cache.commit();
```

**File:** contracts/controller/README.md (L73-78)
```markdown
| `supply` | `fn supply( env: Env, caller: Address, account_id: u64, spoke_id: u32, assets: Vec<(HubAssetKey, i128)>, ) -> u64` | blocked by global pause | Supplies `assets` as collateral to `account_id` in spoke `spoke_id`, creating a new account when `account_id` is 0, and returns the account id. |
| `borrow` | `fn borrow( env: Env, caller: Address, account_id: u64, borrows: Vec<(HubAssetKey, i128)>, to: Option<Address>, )` | blocked by global pause | Borrows `borrows` against `account_id`'s collateral, sending the funds to `to` if provided or to the caller otherwise; reverts if the resulting position breaches the account's solvency limits. |
| `withdraw` | `fn withdraw( env: Env, caller: Address, account_id: u64, withdrawals: Vec<(HubAssetKey, i128)>, to: Option<Address>, ) -> Vec<(HubAssetKey, i128)>` | — | Withdraws `withdrawals` from `account_id`'s supplied collateral, sending the funds to `to` if provided or to the caller otherwise, and returns the amounts actually withdrawn; a zero amount for an asset withdraws the entire position. |
| `repay` | `fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>)` | — | Repays `payments` against `account_id`'s debt positions, pulling the funds from the caller and refunding any excess. |
| `liquidate` | `fn liquidate( env: Env, liquidator: Address, account_id: u64, debt_payments: Vec<(HubAssetKey, i128)>, seize_mode: SeizeMode, ) -> u64` | — | Liquidates `account_id` by having `liquidator` repay `debt_payments` and seizing collateral at a bonus scaled by the account's health factor. Returns the `Credit` receiver's account id, or 0 for `Transfer`. |
| `clean_bad_debt` | `fn clean_bad_debt(env: Env, caller: Address, account_id: u64)` | — | Socializes `account_id`'s debt into the supply index and removes the account when it is insolvent and its remaining collateral value is at or below the dust threshold; reverts otherwise. |
```
