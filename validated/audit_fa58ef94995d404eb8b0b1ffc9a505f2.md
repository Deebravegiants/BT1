### Title
Supply-index floor resurrects wiped-out supplier claims after bad-debt cleanup - (File: contracts/pool/src/interest.rs)

### Summary
`apply_bad_debt_to_supply_index` caps a write-down at the market’s total supplied value but then clamps the resulting supply index to `SUPPLY_INDEX_FLOOR_RAW`, rather than allowing it to reach zero. Consequently, every surviving supply share retains approximately 0.1% of its pre-cleanup claim even when the bad debt exhausted the market’s entire supplier backing.

A surviving supplier can later withdraw that residual claim after another borrower repays debt or a caller recapitalizes the market. Ordinary `supply` cannot seed the market because it checks `require_backed_market`, but repayment and recapitalization can create cash while withdrawal only requires sufficient reserves.

### Finding Description
During permissionless `Controller::clean_bad_debt(caller, account_id)`, the controller submits each borrow leg to `pool_seize_positions_call` and then deletes the account. [1](#0-0) [2](#0-1) 

For each `AccountPositionType::Borrow` entry, the pool converts the scaled debt to a ceil-valued RAY amount, applies it as a supply-index write-down, and burns the debt shares. [3](#0-2) 

The root cause is in `apply_bad_debt_to_supply_index`: `capped = min(bad_debt, total_supplied_value)` correctly limits the write-down to the entire supplier base, but `new_supply_index.max(SUPPLY_INDEX_FLOOR_RAW)` raises an intended zero index back to `RAY / 1000`. [4](#0-3) 

The share total is not correspondingly burned or reduced for unrelated surviving suppliers. Their scaled positions remain valid, and withdrawals convert those shares through the clamped index using `resolve_withdrawal`. [5](#0-4)  The withdraw path enforces cash availability and only checks the narrower `require_supply_for_debt` guard, not `require_backed_market`, before debiting cash and transferring tokens. [6](#0-5) 

The repository’s own pool test demonstrates this residual-claim behavior: after a write-down exceeding total supply, the index is clamped to the floor, a stranded claim remains positive, and once cash exists, withdrawal pays that claim. [7](#0-6) 

### Impact Explanation
This can permanently impair or drain a market that was supposed to have been completely written down.

After the write-down, cash added by an unrelated borrower’s `Controller::repay` or by `Controller::recapitalize` becomes withdrawable by accounts whose economic claim should have been zero. `repay` is permissionless, and `recapitalize` explicitly injects measured backing up to the market’s shortfall. [8](#0-7) [9](#0-8) 

A holder of surviving supply shares can call:

```text
withdraw(
  caller = surviving_supplier,
  account_id = supplier_account,
  withdrawals = [(debt_market_hub_asset, 0)],
  to = None
)
```

The zero amount is the withdraw-all sentinel, and the pool pays the floor-scaled residual claim. [10](#0-9) [11](#0-10) 

The extracted assets should have remained backing for still-outstanding debt or for the recapitalization shortfall. Depending on scale, this is theft of user repayments or recapitalized funds and leaves the market insolvent.

### Likelihood Explanation
The condition requires bad debt whose ceil-valued amount reaches or exceeds the total floor-valued supplier base, which can occur once accrued borrower debt outgrows supplier claims. Permissionless `clean_bad_debt` then triggers the write-down whenever the target still has debt, is insolvent, and has no more than the protocol’s dust collateral threshold. [12](#0-11) 

The attacker only needs to have held an unrelated surviving supply position before cleanup; no privileged role, leaked key, invalid oracle, or reentrancy is required. A later third-party repayment or recapitalization is sufficient to create withdrawable cash.

One mitigating constraint is that `supply` checks the whole market for an existing backing shortfall before minting new shares. [13](#0-12)  Therefore, the cash source generally must be debt repayment or recapitalization rather than a fresh deposit.

### Recommendation
Do not impose a nonzero supply-index floor when the capped write-down consumes all supplier value.

When `remaining == 0`, either:

- set the supply index to zero and require all outstanding supply claims to resolve to zero, or
- explicitly burn all surviving supply shares and atomically remove the corresponding accounts/claims before allowing further market settlement.

If the floor exists to prevent division by zero, share conversion must special-case a wiped market so `scaled > 0` produces zero asset value until the market is reset or recapitalized under an explicit migration path. Add an end-to-end regression test in which bad debt exceeds total supply, a surviving supplier calls `withdraw`, and unrelated repayment or recapitalized cash cannot be extracted as residual yield.

### Proof of Concept
The existing unit test already proves the arithmetic failure:

```rust
// contracts/pool/tests/interest.rs
apply_bad_debt_to_supply_index(&mut cache, bad_debt);
cache.burn_debt(borrow_scaled);

assert_eq!(
    cache.supply_index().raw(),
    SUPPLY_INDEX_FLOOR_RAW,
);

let alice_stranded = cache.unscale_supply_floor(alice_scaled);
assert!(alice_stranded > 0);

let (burn, gross) = cache.resolve_withdrawal(i128::MAX, alice_scaled);
cache.require_reserves(gross);
cache.burn_supply(burn);
cache.debit_cash(gross);

assert!(gross > 0);
``` [14](#0-13) 

Production sequence:

1. A market contains supplier `S` and borrower `A`.
2. Interest or multiple borrow positions make `A`’s debt exceed the market’s total supplied value.
3. `A` becomes insolvent with collateral at or below the dust threshold.
4. Any caller invokes `clean_bad_debt(caller, A_account_id)`.
5. The pool caps the write-down at total supplied value but clamps `supply_index` to `RAY / 1000`.
6. `S` retains its original scaled supply position with a positive residual claim.
7. Another borrower repays debt, or a user calls `recapitalize`, producing cash.
8. `S` calls `withdraw(..., [(hub_asset, 0)], ...)`.
9. The pool resolves the floor-scaled claim, burns `S`’s shares, and transfers cash that should have backed the remaining debt or recapitalization shortfall.

### Citations

**File:** contracts/controller/src/lib.rs (L130-134)
```rust
    /// Repays `account_id`'s debt using measured payments from the caller.
    /// Anyone may repay; excess payments are refunded to the caller.
    fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>) {
        positions::process_repay(&env, &caller, account_id, &payments);
    }
```

**File:** contracts/controller/src/lib.rs (L160-165)
```rust
    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
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

**File:** contracts/pool/src/cache/scale.rs (L94-105)
```rust
    /// Resolves a withdrawal request into (shares burned, gross asset amount).
    ///
    /// Caps against `pos_scaled` so the user cannot withdraw more than held.
    pub(crate) fn resolve_withdrawal(&self, amount: i128, pos_scaled: Ray) -> (Ray, i128) {
        resolve_withdrawal(
            &self.env,
            amount,
            pos_scaled,
            self.supply_index,
            self.params.asset_decimals,
        )
    }
```

**File:** contracts/pool/src/ops/withdraw.rs (L111-119)
```rust
fn gate_and_debit(env: &Env, cache: &mut Cache, net_transfer: i128, skip_utilization_check: bool) {
    cache.require_reserves(net_transfer);

    if !skip_utilization_check {
        guards::require_utilization_below_max(env, cache);
    }
    guards::require_supply_for_debt(env, cache);
    cache.debit_cash(net_transfer);
}
```

**File:** contracts/pool/tests/interest.rs (L431-485)
```rust
fn test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard() {
    let t = TestSetup::new();
    t.as_contract(|| {
        let alice_scaled_raw = 1_000 * RAY;
        let borrowed_scaled_raw = 1_000 * RAY;
        let mut cache = t.fresh_cache(PoolStateRaw {
            supplied: alice_scaled_raw,
            borrowed: borrowed_scaled_raw,
            revenue: 0,
            borrow_index: RAY,
            supply_index: RAY,
            last_timestamp: 0,
            cash: 0,
        });
        let alice_scaled = Ray::from(alice_scaled_raw);
        let borrow_scaled = Ray::from(borrowed_scaled_raw);

        let bad_debt = cache.unscale_borrow_ceil_ray(borrow_scaled);
        apply_bad_debt_to_supply_index(&mut cache, bad_debt);
        cache.burn_debt(borrow_scaled);

        assert_eq!(
            cache.supply_index().raw(),
            SUPPLY_INDEX_FLOOR_RAW,
            "seize wipeout clamps supply_index UP to RAY/1000, leaving unburned shares a residual"
        );

        let alice_stranded = cache.unscale_supply_floor(alice_scaled);
        assert!(alice_stranded > 0, "wiped survivor keeps a stranded claim");
        assert_eq!(
            cache.cash(),
            0,
            "empty market: claim masked by require_reserves"
        );

        let deposit = alice_stranded;
        let bob_scaled = cache.calculate_scaled_supply(deposit);
        cache.mint_supply(bob_scaled);
        cache.credit_cash(deposit);

        let total_owed = cache.unscale_supply_floor(cache.supplied());
        assert!(
            total_owed > cache.cash(),
            "post-deposit books insolvent: owed {} > cash {}",
            total_owed,
            cache.cash()
        );

        let (burn, gross) = cache.resolve_withdrawal(i128::MAX, alice_scaled);
        cache.require_reserves(gross);
        cache.burn_supply(burn);
        cache.debit_cash(gross);

        assert!(gross > 0, "wiped position pays out real cash");
        assert_eq!(gross, deposit, "Alice extracts exactly Bob's fresh deposit");
```

**File:** contracts/pool/src/lib.rs (L182-193)
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
```

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

**File:** contracts/controller/src/positions/supply.rs (L181-199)
```rust
    for (hub_asset, amount) in aggregated.iter() {
        enforce_spoke_asset_flags(
            env,
            cache,
            account.spoke_id,
            &hub_asset,
            FreezePolicy::AllowOnExit,
        );
        let position = get_supply_position_or_panic(env, account, &hub_asset);
        let requested = if amount == 0 {
            WITHDRAW_ALL_SENTINEL
        } else {
            amount
        };
        entries.push_back(PoolWithdrawEntry {
            action: make_pool_action(&position, requested, hub_asset.clone()),
            protocol_fee: 0,
        });
    }
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L211-238)
```rust
/// Requires open debt and the selected insolvency gate, then cleans up the account.
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

**File:** contracts/pool/src/ops/supply.rs (L23-38)
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
```
