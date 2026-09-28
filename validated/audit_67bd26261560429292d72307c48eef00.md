### Title
Bad-debt write-down leaves unbacked supply claims by clamping a wiped market to the supply-index floor - (File: contracts/pool/src/interest.rs)

### Summary

`apply_bad_debt_to_supply_index` caps the write-down at the full supplied value, but then raises a fully written-down index back to `SUPPLY_INDEX_FLOOR_RAW` instead of allowing it to reach zero. Consequently, a bad-debt seizure that consumes all supplier value leaves every supply share with a residual claim despite there being no corresponding backing. `clean_bad_debt` is permissionless once the affected account has open debt and only dust collateral, so an unprivileged caller can trigger this state transition. [1](#0-0) [2](#0-1) 

### Finding Description

During `clean_bad_debt`, the controller converts every remaining account supply and borrow position into a `PoolSeizeEntry` and sends the batch to the pool. [3](#0-2)  For each borrow-side entry, `ops::seize::apply` converts the scaled debt to its ceiled asset value, passes that amount to `apply_bad_debt_to_supply_index`, and burns the debt shares. [4](#0-3) 

`apply_bad_debt_to_supply_index` correctly caps the loss at `total_supplied_value`, computes the surviving fraction, and multiplies the current supply index by that fraction. However, it then applies `new_supply_index.max(SUPPLY_INDEX_FLOOR_RAW)`. [2](#0-1)  Therefore, when bad debt is greater than or equal to the entire supplied value, `reduction_factor` is zero and `new_supply_index` is zero, but the final stored index becomes approximately `RAY / 1000`.

The scaled-share balances are not reduced. Every existing supply share continues to unscale to roughly 0.1% of its pre-write-down claim even though the full supplier value was socialized as bad debt. This creates a persistent backing shortfall because `backing_shortfall` compares the floored total supply claim against `cash + outstanding_debt`. [5](#0-4) 

The subsequent market behavior is inconsistent:

- `supply` rejects entry while the phantom shortfall exists through `require_backed_market`. [6](#0-5) 
- `withdraw` can pay the residual claims once any cash exists, even though those claims were supposed to have been fully written down.
- `recapitalize` treats the phantom residual as a real shortfall and credits donated cash to cover it. [7](#0-6) 

The repository’s own raw-cache regression tests explicitly model this outcome: after a write-down larger than supplied value, the floor leaves a positive stranded claim that can consume subsequently credited cash. [8](#0-7) 

### Impact Explanation

This is accounting corruption following a memory-corruption-style invalid state transition. A complete supplier write-down does not actually clear supplier claims; it converts them into an unbacked residual liability.

The immediate result is a market insolvency and temporary operational freeze: new supply is rejected by `require_backed_market`, withdrawals cannot be paid while cash is absent, and borrowing is unavailable until the residual is covered. [9](#0-8) [10](#0-9) 

If anyone uses the permissionless `recapitalize` entrypoint to restore the market, part of the recapitalization can fund claims that should have been reduced to zero. [11](#0-10) [12](#0-11)  Thus, the floor can convert recapitalization funds into payouts for wiped-out supply positions. Because the residual is only 0.1% of supplier value and requires a complete market write-down, the practical severity is Medium rather than Critical or High.

### Likelihood Explanation

An unprivileged address can reach the vulnerable write-down through `liquidate` or `clean_bad_debt`; `clean_bad_debt` only requires caller authorization, an open borrow position, insolvency, and remaining collateral at or below the dust cap. [13](#0-12) [14](#0-13) 

The trigger requires bad debt at least equal to the market’s total supplied value. This is not an arbitrary user input and generally requires a severe collateral collapse or an already thin market with outsized unbacked debt. Once that condition exists, however, the bug is deterministic: `bad_debt >= total_supplied_value` always produces `reduction_factor == 0`, after which the floor raises the index back to `RAY / 1000`. [2](#0-1) 

### Recommendation

Do not clamp a fully exhausted supply index upward to `SUPPLY_INDEX_FLOOR_RAW`. Either:

1. allow `new_supply_index` to become zero when `remaining == 0`, and define withdrawal/supply semantics for a zero-index wiped market; or
2. burn or otherwise clear the corresponding scaled supply shares when the computed reduction reaches zero; or
3. restrict the floor to partial write-downs only, for example:

```rust
let new_supply_index = cache
    .supply_index()
    .mul_floor(cache.env(), reduction_factor);

let corrected = if remaining == Ray::ZERO {
    Ray::ZERO
} else {
    new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))
};

cache.set_supply_index(corrected);
```

The implementation should preserve an explicit invariant that after `bad_debt >= supplied * supply_index`, total supplier claims are zero or exactly equal to available backing. Add an end-to-end controller test that creates wipeout bad debt through `clean_bad_debt`, verifies the post-cleanup backing shortfall is zero, and verifies that `recapitalize` applies zero to the phantom residual.

### Proof of Concept

1. Establish a market where a user has open debt and the total supplied value is small relative to that debt.
2. Make the position insolvent, for example through a collateral price decline, while leaving collateral at or below the cleanup dust threshold.
3. Call `Controller::clean_bad_debt(caller, account_id)`. This is permissionless once the dust-capped insolvency gate is satisfied. [1](#0-0) 
4. The controller emits borrow-side `PoolSeizeEntry` records and invokes `LiquidityPool::seize_positions`. [15](#0-14) 
5. The pool computes `bad_debt = unscale_borrow_ceil(position)` and calls `apply_bad_debt_to_supply_index`. [4](#0-3) 
6. With `bad_debt >= supplied * supply_index`, `capped` equals `total_supplied_value`, so `remaining` and `reduction_factor` are zero. [16](#0-15) 
7. `new_supply_index` is zero, but line 88 stores `SUPPLY_INDEX_FLOOR_RAW` instead. [17](#0-16) 
8. Existing scaled supply balances remain nonzero and now unscale to approximately 0.1% of their original value despite the market having no backing. `backing_shortfall` therefore remains positive. [5](#0-4) 
9. A later `recapitalize` call credits cash up to that artificial shortfall. [12](#0-11) 
10. A holder of the wiped-out supply shares can then withdraw against the recapitalized cash, receiving value that should have been socialized away.

### Citations

**File:** contracts/controller/src/lib.rs (L160-165)
```rust
    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
    }
```

**File:** contracts/controller/src/lib.rs (L390-395)
```rust
    /// Covers a pool backing shortfall using measured receipts from `payer`.
    /// Refunds excess and returns the amount applied in asset units.
    /// Permissionless; requires payer authorization.
    fn recapitalize(env: Env, payer: Address, hub_asset: HubAssetKey, amount: i128) -> i128 {
        markets::recapitalize(&env, payer, hub_asset, amount)
    }
```

**File:** contracts/pool/src/interest.rs (L80-88)
```rust
    let capped = bad_debt.min(total_supplied_value);
    let remaining = total_supplied_value.checked_sub(cache.env(), capped);

    let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
    let new_supply_index = cache
        .supply_index()
        .mul_floor(cache.env(), reduction_factor);

    cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
```

**File:** contracts/controller/src/positions/liquidation/bad_debt.rs (L21-49)
```rust
    let mut entries: Vec<PoolSeizeEntry> = Vec::new(env);
    for (hub_asset, position) in iter_typed_positions(&account.supply_positions) {
        cache.apply_spoke_exit(
            account.spoke_id,
            UsageSide::Supply,
            &hub_asset,
            position.scaled_amount,
        );
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Deposit,
            position: (&position).into(),
        });
    }
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

**File:** contracts/pool/src/guards.rs (L61-65)
```rust
pub(crate) fn backing_shortfall(cache: &Cache) -> i128 {
    let supplied_claim = cache.unscale_supply_floor(cache.supplied());
    let outstanding_debt = cache.unscale_borrow_ceil(cache.borrowed());
    let backing = cache.cash().saturating_add(outstanding_debt);
    supplied_claim.saturating_sub(backing).max(0)
```

**File:** contracts/pool/src/ops/supply.rs (L23-30)
```rust
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    guards::require_backed_market(env, &cache);

    let minted = cache.calculate_scaled_supply(amount);
    assert_with_error!(
        env,
```

**File:** contracts/pool/src/ops/recapitalize.rs (L49-58)
```rust
    require_nonneg_amount(env, amount);
    let mut cache = ops::renewed_market(env, &hub_asset);

    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();
```

**File:** contracts/pool/tests/interest.rs (L332-360)
```rust
        apply_bad_debt_to_supply_index(&mut cache, Ray::from(2_000_000 * RAY));
        assert_eq!(
            cache.supply_index().raw(),
            SUPPLY_INDEX_FLOOR_RAW,
            "wipeout must clamp supply index UP to the floor, not reset the base"
        );

        let stranded = cache.unscale_supply_floor(scaled_a);
        assert!(stranded > 0, "floor clamp leaves userA a phantom claim");
        assert_eq!(cache.cash(), 0, "empty market: no cash to extract yet");

        let c = stranded;
        let scaled_b = cache.calculate_scaled_supply(c);
        cache.mint_supply(scaled_b);
        cache.credit_cash(c);

        let b_claim = cache.unscale_supply_floor(scaled_b);
        assert_eq!(b_claim, c, "userB's honest claim equals their deposit");

        let (burn, gross) = cache.resolve_withdrawal(i128::MAX, scaled_a);
        cache.require_reserves(gross);
        cache.burn_supply(burn);
        cache.debit_cash(gross);

        assert!(gross > 0, "stranded position pays out non-zero");
        assert_eq!(
            gross, c,
            "userA drains exactly userB's fresh deposit out of the pool"
        );
```

**File:** contracts/pool/src/cache/cash.rs (L15-20)
```rust
    pub(crate) fn require_reserves(&self, amount: i128) {
        assert_with_error!(
            self.env,
            self.cash >= amount,
            CollateralError::InsufficientLiquidity
        );
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-199)
```rust
/// Authorizes permissionless dust-gated cleanup outside flash loans.
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L216-237)
```rust
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
