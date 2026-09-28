### Title
Unrealized bad debt lets suppliers withdraw at full value and concentrate losses - ([File: contracts/pool/src/guards.rs](contracts/pool/src/guards.rs))

### Summary

A supplier can withdraw at the pre-socialization supply index after an account has become insolvent but before a liquidation or `clean_bad_debt` call writes the bad debt into the market. Because pool backing treats outstanding debt at full face value until seizure, early exits receive cash that should already be haircut by the known bad debt. The later `supply_index` write-down is then borne entirely by suppliers who did not exit.

### Finding Description

`Controller::withdraw` resolves supplier shares through the pool at the current `supply_index`; the controller only checks the withdrawing account’s post-withdrawal solvency, not whether another account’s pending bad debt should already reduce all supplier claims [1](#0-0) .

The pool’s backing calculation counts outstanding debt at face value as backing:

```rust
let backing = cache.cash().saturating_add(outstanding_debt);
supplied_claim.saturating_sub(backing).max(0)
``` [2](#0-1) 

Consequently, once an account is economically insolvent but before `liquidate` or `clean_bad_debt` executes, the market still reports itself backed. A supplier may withdraw available cash at the unwritten-down index. Only later does `apply_bad_debt_to_supply_index` reduce `supply_index`, applying the entire loss to the scaled supply remaining after the exit [3](#0-2) .

The issue is reachable without privileges because `withdraw` is available to the account owner, `update_indexes` is permissionless, and `liquidate`/`clean_bad_debt` can be invoked after the withdrawal [4](#0-3) . Permissionless cleanup requires outstanding debt and the configured insolvency/dust gate [5](#0-4) .

### Impact Explanation

Remaining suppliers permanently lose more than their pro-rata share of bad debt. In severe cases, an early supplier can remove most available cash and leave the residual suppliers to absorb a write-down approaching the full remaining supply value.

For example:

- Pool has 100 units supplied: attacker owns 75, another supplier owns 25.
- A borrower account controlled by the same attacker has borrowed 30.
- The account later becomes deeply insolvent, so the 30 units of debt are unrecoverable.
- Before liquidation or cleanup, the attacker withdraws 65 units, subject to the market’s utilization limit.
- Only 35 units of scaled supply remain; the subsequent 30-unit bad-debt write-down is concentrated on that remainder.

Absent the early exit, the attacker’s fair share of the 30-unit loss was 22.5 units. By withdrawing first, the attacker recovers substantially more than the post-loss value of their position, while the other supplier absorbs most or all of the loss.

### Likelihood Explanation

Likelihood is Medium. Exploitation requires a pending insolvent account and enough free pool cash for the supplier withdrawal. An unprivileged user can control both a supplier account and a borrower account, monitor the borrower’s health factor, call `update_indexes`, withdraw before the write-down, and then invoke `liquidate` or `clean_bad_debt`. The setup is constrained by collateral value, market utilization, liquidity, and the bad-debt admission gates, but does not require privileged access or an authorization bypass.

### Recommendation

Account for known insolvent debt before allowing ordinary withdrawals. Possible fixes include:

- Add a controller-level check that blocks or haircuts non-liquidation withdrawals while any account satisfies the bad-debt liquidation condition.
- Realize pending bad debt in the affected markets before processing withdrawals.
- Maintain a pending-loss reserve based on liquidation estimates and subtract it from supplier claim backing.
- Prevent suppliers from reducing utilization when a permissionless liquidation or cleanup is already available, or process cleanup atomically before the withdrawal.

The selected fix should preserve the invariant that bad debt is allocated across the supplier base present when the insolvency became actionable, rather than only the suppliers remaining after a withdrawal race.

### Proof of Concept

Assuming `ETH` is the debt market and the attacker controls both `supplier_id` and `borrower_id`:

```text
1. Attacker supplies 75 ETH through:
   supply(attacker, 0, spoke_id, [(eth_hub_asset, 75)])

2. Another supplier supplies 25 ETH.

3. Attacker's borrower account supplies collateral and borrows 30 ETH:
   supply(attacker, 0, spoke_id, [(collateral_hub_asset, collateral)])
   borrow(attacker, borrower_id, [(eth_hub_asset, 30)], Some(attacker))

4. Market movement or accrued interest makes borrower_id insolvent.

5. Before the bad debt is realized, attacker calls:
   update_indexes(attacker, [eth_hub_asset])
   withdraw(
       attacker,
       supplier_id,
       [(eth_hub_asset, 65)],
       Some(attacker)
   )

   The pool still counts the 30 ETH debt as full backing, so the withdrawal
   uses the pre-write-down supply index.

6. Attacker then invokes liquidation, or when the collateral gate permits:
   clean_bad_debt(attacker, borrower_id)

7. Pool seize processing calls apply_bad_debt_to_supply_index, reducing the
   supply index only for the suppliers that remain after the withdrawal.
```

The economic defect is demonstrated by the repository’s own scenario documenting that a supplier can exit at the unwritten-down index and amplify losses onto remaining suppliers [6](#0-5) .

### Citations

**File:** contracts/controller/src/positions/supply.rs (L140-158)
```rust
pub(crate) fn process_withdraw(
    env: &Env,
    caller: &Address,
    account_id: u64,
    withdrawals: &Vec<HubPayment>,
    to: Option<Address>,
) -> Vec<HubPayment> {
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_payments(env, withdrawals, payments::ZeroLeg::MeansAll);

    let paid = settle_withdraw(env, &mut account, &recipient, &aggregated, &mut cache);
    let _ = enforce_post_pool_solvency(env, &mut cache, &mut account);
```

**File:** contracts/pool/src/guards.rs (L60-66)
```rust
/// Asset units by which supplier claims exceed cash + debt (0 if solvent).
pub(crate) fn backing_shortfall(cache: &Cache) -> i128 {
    let supplied_claim = cache.unscale_supply_floor(cache.supplied());
    let outstanding_debt = cache.unscale_borrow_ceil(cache.borrowed());
    let backing = cache.cash().saturating_add(outstanding_debt);
    supplied_claim.saturating_sub(backing).max(0)
}
```

**File:** contracts/pool/src/interest.rs (L73-88)
```rust
pub(crate) fn apply_bad_debt_to_supply_index(cache: &mut Cache, bad_debt: Ray) {
    let total_supplied_value = cache.supplied().mul(cache.env(), cache.supply_index());

    if total_supplied_value == Ray::ZERO {
        return;
    }

    let capped = bad_debt.min(total_supplied_value);
    let remaining = total_supplied_value.checked_sub(cache.env(), capped);

    let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
    let new_supply_index = cache
        .supply_index()
        .mul_floor(cache.env(), reduction_factor);

    cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
```

**File:** contracts/controller/src/lib.rs (L120-164)
```rust
    fn withdraw(
        env: Env,
        caller: Address,
        account_id: u64,
        withdrawals: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) -> Vec<(HubAssetKey, i128)> {
        positions::process_withdraw(&env, &caller, account_id, &withdrawals, to)
    }

    /// Repays `account_id`'s debt using measured payments from the caller.
    /// Anyone may repay; excess payments are refunded to the caller.
    fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>) {
        positions::process_repay(&env, &caller, account_id, &payments);
    }

    /// Repays debt and seizes collateral at a health-factor-based bonus.
    /// Permissionless, including self-liquidation; requires liquidator authorization.
    /// Residual bad debt is socialized only at or below the collateral dust cap.
    ///
    /// `Transfer` pays pool cash and returns `0`. `Credit(id)` moves net supply
    /// shares to a different, authorized Normal-mode account on the same spoke;
    /// `Credit(0)` creates one. Credit mode needs no free collateral liquidity
    /// and returns the receiving account id.
    fn liquidate(
        env: Env,
        liquidator: Address,
        account_id: u64,
        debt_payments: Vec<(HubAssetKey, i128)>,
        seize_mode: SeizeMode,
    ) -> u64 {
        positions::liquidation::process_liquidation(
            &env,
            &liquidator,
            account_id,
            &debt_payments,
            seize_mode,
        )
    }

    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L212-237)
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
