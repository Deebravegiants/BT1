### Title
`claim_revenue` forces a maximum claim that can revert and freeze otherwise claimable protocol revenue - (contracts/pool/src/ops/revenue.rs)

### Summary
The controller exposes permissionless `claim_revenue(caller, assets)`, but neither that entrypoint nor the underlying pool call accepts a requested amount. [1](#0-0) [2](#0-1)  The pool always attempts to burn the largest currently cash-backed revenue claim before enforcing the post-claim utilization ceiling. [3](#0-2) [4](#0-3)  If that maximum-sized claim raises utilization above `max_utilization`, the entire transaction reverts even though a smaller claim would satisfy the same invariant. [5](#0-4) 

### Finding Description
`Cache::burn_claimable_revenue` calculates `treasury_actual = floor(revenue * supply_index)` and automatically chooses `amount = min(cash, treasury_actual)`. [6](#0-5)  It then burns either all revenue shares or a cash-limited pro-rata amount, with no caller-controlled way to request less than that maximum. [7](#0-6) 

Because revenue shares are included in total supplied shares, burning them decreases `supplied` while borrowed shares remain unchanged. [8](#0-7) [9](#0-8)  `ops::revenue::accounting` performs this burn before `require_utilization_below_max`, so the check evaluates the most utilization-diluting claim possible. [3](#0-2)  The guard computes `ceil(borrowed_value / supplied_value)` and rejects when it exceeds the market ceiling. [5](#0-4) 

This creates the same “all-or-nothing” shape as the reported bug: the operation can fail solely because it insists on the maximum recoverable amount rather than allowing a safe partial amount. [10](#0-9) [4](#0-3) 

### Impact Explanation
Unclaimed protocol revenue can remain temporarily frozen even when a nonzero amount could be paid without breaching utilization. [11](#0-10) [12](#0-11)  The accumulator receives nothing on a revert, while the revenue shares remain inside the pool and continue accruing rather than being distributable. [13](#0-12) [14](#0-13) 

The freeze persists until borrowers repay, new supply enters, indexes change favorably, or market parameters change. [5](#0-4)  An unprivileged user can reach the failing path through `Controller::claim_revenue`; the call itself only requires caller authorization. [1](#0-0) [15](#0-14) 

### Likelihood Explanation
The state is reachable through normal protocol activity: protocol revenue accrues from borrowing, while ordinary borrowers can drive utilization near the configured ceiling. [16](#0-15) [8](#0-7)  Interest accrual can subsequently increase debt value without any privileged action. [17](#0-16) 

The repository contains a regression test for precisely this condition: with supplied shares of `100 * RAY`, borrowed shares of `90 * RAY`, revenue of `10 * RAY`, cash of 10 units, and a 95% ceiling, `claim_revenue` reverts with `UtilizationAboveMax`. [18](#0-17)  In that simplified state, claiming 5 units would leave utilization at `90 / 95`, within the same ceiling, but the interface provides no way to request that amount. [4](#0-3) [2](#0-1) 

### Recommendation
Add an explicit `max_amount` or `amount` argument to `Controller::claim_revenue` and `LiquidityPool::claim_revenue`, and cap the pool payout as `min(requested_amount, cash, floor(revenue_value))` before burning the corresponding pro-rata revenue shares. [1](#0-0) [4](#0-3) 

The existing proportional-share logic already supports cash-limited partial claims, so it can be reused with the caller-provided cap. [19](#0-18)  The post-claim utilization and no-debt-without-supply guards should still run after the bounded burn. [11](#0-10) 

### Proof of Concept
Assume a listed market with indexes at `1.0`, `max_utilization = 0.95`, total supply shares of `100`, debt shares of `90`, revenue shares of `10`, and cash of at least 10 units. [20](#0-19) 

```rust
// Any caller, after the accumulator has been configured:
controller.claim_revenue(
    caller,
    vec![HubAssetKey { hub_id, asset }],
);
```

The controller routes the request to `pool.claim_revenue(hub_asset)` without an amount parameter. [15](#0-14) [21](#0-20)  The pool selects all 10 units as `min(cash, revenue_value)` and burns all 10 revenue shares, reducing supplied shares from 100 to 90. [4](#0-3) [9](#0-8) 

Post-claim utilization is `90 / 90 = 100%`, so `require_utilization_below_max` reverts against the configured 95% ceiling and rolls back the entire claim. [12](#0-11) [22](#0-21)  A requested claim of 5 units would instead reduce supplied shares to 95 and leave utilization at approximately `94.74%`, demonstrating that nonzero revenue was safely claimable but unreachable through the fixed maximum-claim API. [19](#0-18) [2](#0-1)

### Citations

**File:** contracts/controller/src/lib.rs (L374-379)
```rust
    /// Claims pool revenue and forwards measured receipts to the accumulator.
    /// Returns those amounts in asset units, in input order. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn claim_revenue(env: Env, caller: Address, assets: Vec<HubAssetKey>) -> Vec<i128> {
        markets::claim_revenue(&env, caller, assets)
```

**File:** contracts/pool/src/lib.rs (L135-147)
```rust
    /// Batch-borrows assets and transfers them to `receiver`: accrues
    /// interest, mints scaled debt, debits cash, and enforces max
    /// utilization after each mint. Restricted to the owner; returns one
    /// [`PoolPositionMutation`] per entry.
    #[only_owner]
    fn borrow(
        env: Env,
        receiver: Address,
        entries: Vec<PoolBorrowEntry>,
    ) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, |env, entry| {
            ops::borrow::apply(env, &receiver, entry)
        })
```

**File:** contracts/pool/src/lib.rs (L174-180)
```rust
    /// Accrues interest for each market in `hub_assets` through the current
    /// ledger time. Commits state even with no elapsed time to reserve the write
    /// footprint, and emits its market state event. Restricted to the owner.
    #[only_owner]
    fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>) {
        ops::market::accrue(&env, hub_assets);
    }
```

**File:** contracts/pool/src/lib.rs (L243-251)
```rust
    /// Burns claimable revenue shares, debits cash and pays the owner the lesser
    /// of cash and revenue's floored token value. Returns zero when nothing is
    /// claimable. Owner-only.
    ///
    /// Decrements the snapshot `revenue` field, so that field is not a
    /// cumulative counter.
    #[only_owner]
    fn claim_revenue(env: Env, hub_asset: HubAssetKey) -> PoolAmountMutation {
        ops::revenue::apply(&env, hub_asset)
```

**File:** contracts/pool/src/ops/revenue.rs (L19-23)
```rust
/// Claims all currently claimable revenue and pays it to the Ownable owner.
/// Emits a market state snapshot in all cases. If nothing is claimable, returns
/// a mutation with `actual_amount` zero and performs no transfer.
pub(crate) fn apply(env: &Env, hub_asset: HubAssetKey) -> PoolAmountMutation {
    let outcome = accounting(env, hub_asset);
```

**File:** contracts/pool/src/ops/revenue.rs (L39-46)
```rust
pub(crate) fn accounting(env: &Env, hub_asset: HubAssetKey) -> RevenueOutcome {
    let mut cache = ops::renewed_market(env, &hub_asset);

    let net_transfer = cache.burn_claimable_revenue();

    guards::require_utilization_below_max(env, &cache);
    guards::require_supply_for_debt(env, &cache);
    cache.debit_cash(net_transfer);
```

**File:** contracts/pool/src/cache/shares.rs (L35-39)
```rust
    /// Mints protocol revenue shares (also increases total supply).
    pub(crate) fn accrue_revenue(&mut self, scaled: Ray) {
        self.revenue = self.revenue.checked_add(&self.env, scaled);
        self.supplied = self.supplied.checked_add(&self.env, scaled);
    }
```

**File:** contracts/pool/src/cache/shares.rs (L54-74)
```rust
    pub(crate) fn burn_claimable_revenue(&mut self) -> i128 {
        let treasury_actual = self.unscale_supply_floor(self.revenue);
        let amount = self.cash.min(treasury_actual);
        if amount <= 0 {
            return 0;
        }
        let scaled_to_burn = if amount >= treasury_actual {
            self.revenue
        } else {
            self.revenue
                .mul_ratio_ceil(&self.env, amount, treasury_actual)
        };

        assert_with_error!(
            self.env,
            scaled_to_burn != Ray::ZERO,
            GenericError::InternalError
        );
        self.revenue = self.revenue.checked_sub(&self.env, scaled_to_burn);
        self.supplied = self.supplied.checked_sub(&self.env, scaled_to_burn);
        amount
```

**File:** contracts/pool/src/guards.rs (L24-32)
```rust
    let borrowed = cache.borrowed().mul_ceil(env, cache.borrow_index());
    if borrowed == Ray::ZERO {
        return;
    }
    let supplied = cache.supplied().mul_floor(env, cache.supply_index());
    assert_with_error!(
        env,
        supplied > Ray::ZERO && borrowed.div_ceil(env, supplied) <= cache.params().max_utilization,
        CollateralError::UtilizationAboveMax
```

**File:** contracts/controller/src/markets.rs (L129-135)
```rust
pub(crate) fn claim_revenue(env: &Env, caller: Address, assets: Vec<HubAssetKey>) -> Vec<i128> {
    validation::require_authorized_caller(env, &caller);
    let mut results = Vec::new(env);
    let mut cache = Context::new(env);
    for hub_asset in assets {
        let amount = claim_revenue_for_asset(env, &caller, &hub_asset, &mut cache);
        results.push_back(amount);
```

**File:** contracts/controller/src/markets.rs (L184-196)
```rust
    let _ = pool_claim_revenue_call(env, &pool_addr, hub_asset);

    let received = balance_delta_since(env, asset, &controller, before);

    if received > 0 {
        payments::transfer_amount_measured(
            env,
            asset,
            &controller,
            &accumulator,
            received,
            GenericError::AmountMustBePositive,
        );
```

**File:** contracts/pool/README.md (L337-345)
```markdown
**`claim_revenue`** is capped by cash. `Cache::burn_claimable_revenue` claims
`min(cash, floor(revenue_value))`, so a fully lent-out market pays out less than
`get_revenue` reports, and pays out zero when `cash` is zero. A partial claim
burns revenue shares with `mul_ratio_ceil`, which burns slightly more shares
than the proportional amount. Nothing is lost: the unclaimed remainder stays as
revenue shares and keeps earning. `require_utilization_below_max` and
`require_supply_for_debt` run even when nothing is claimable. If they pass, the
call returns `actual_amount = 0`, moves no tokens, and emits a market state
snapshot. Always read `actual_amount` from the returned `PoolAmountMutation`;
```

**File:** contracts/pool/tests/flows.rs (L1739-1758)
```rust
#[test]
fn test_claim_revenue_rejects_utilization_above_max_after_revenue_burn() {
    let t = TestSetup::new();
    let client = t.client();

    t.env.as_contract(&t.pool, || {
        let key = PoolKey::Params(hub(&t.asset));
        let mut params: MarketParamsRaw = t.env.storage().persistent().get(&key).unwrap();
        params.max_utilization = RAY * 95 / 100;
        t.env.storage().persistent().set(&key, &params);
    });
    t.edit_state(|state| {
        state.supplied = 100 * RAY;
        state.borrowed = 90 * RAY;
        state.revenue = 10 * RAY;
        state.cash = 10_0000000i128;
    });

    let result = flatten_contract_result(client.try_claim_revenue(&hub(&t.asset)));
    assert_contract_error(result, CollateralError::UtilizationAboveMax as u32);
```

**File:** contracts/controller/src/external/pool.rs (L118-125)
```rust
/// Claims accrued revenue to the pool owner (the controller). Returns the pool
/// mutation; callers must measure the controller's actual receipt.
pub(crate) fn pool_claim_revenue_call(
    env: &Env,
    pool_addr: &Address,
    hub_asset: &HubAssetKey,
) -> PoolAmountMutation {
    LiquidityPoolClient::new(env, pool_addr).claim_revenue(hub_asset)
```
