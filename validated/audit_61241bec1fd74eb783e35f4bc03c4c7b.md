### Title
Debt-value overflow permanently freezes all operations on an oversized market - (File: common/src/rates/index.rs)

### Summary
An unprivileged borrower/supplier can leave a market in a state where the next interest accrual overflows `i128` while converting scaled debt to its RAY-denominated value, causing every subsequent pool operation on that market to revert before repayment, withdrawal, liquidation, or recapitalization can execute. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
The pool accrues interest before each market mutation by running `global_sync`, which applies `accrue_step` to the market's scaled `borrowed`, `supplied`, `borrow_index`, and `supply_index`. [4](#0-3) [5](#0-4) 

During accrual, `calculate_supplier_rewards` computes both `borrowed * old_borrow_index` and `borrowed * new_borrow_index`; likewise, utilization conversion calls `scaled_to_original`, which performs `scaled.mul(index)`. [6](#0-5) [7](#0-6) [8](#0-7) 

The borrow index cap is applied only after multiplying `old_index` by the interest factor and does not bound the later `borrowed * new_borrow_index` value calculation. [9](#0-8) 

A market with sufficiently large scaled debt and sustained high utilization can therefore reach an `i128` value overflow before `MAX_BORROW_INDEX_RAY` is reached; the regression test demonstrates `MathOverflow`, followed by failed withdrawals and repayments on the same market. [10](#0-9) 

### Impact Explanation
Once the product `borrowed * borrow_index` exceeds the RAY value domain, the failed multiplication occurs during the mandatory pre-operation accrual rather than in an optional view. [2](#0-1) [11](#0-10) 

Because the accrual aborts before the operation body runs, `repay`, `withdraw`, liquidation withdrawals, `update_indexes`, and other paths touching the affected `(hub_id, asset)` market roll back. [5](#0-4) [12](#0-11) [13](#0-12) 

The result is permanent freezing of supplier cash and borrower collateral associated with the poisoned market, together with loss of the liquidation path needed to protect the pool from insolvency. [14](#0-13) 

### Likelihood Explanation
The attack requires a very large admitted market, near-total utilization, and enough elapsed accrual for the scaled debt value to cross the `i128` RAY ceiling before the index cap. [15](#0-14) [16](#0-15) 

Those conditions are economically demanding, but they are reachable through ordinary unprivileged `supply` and `borrow` calls when configured caps and token liquidity admit the required principal. [17](#0-16) [18](#0-17) 

No privileged call, oracle manipulation, malformed token, or contract upgrade is required after the market configuration admits the exposure. [19](#0-18) [20](#0-19) 

### Recommendation
Bound debt-value multiplication before growing the borrow index, or cap `borrowed` based on the maximum representable `borrowed * MAX_BORROW_INDEX_RAY` value rather than relying on the index ceiling. [9](#0-8) [11](#0-10) 

Borrow entry should additionally reject any scaled debt whose value can overflow during a later maximum-index accrual, and market-cap validation should account for both token-domain and RAY-domain capacity. [21](#0-20) [22](#0-21) 

For already-created markets, add a fail-safe path that can repay or write down debt without recalculating the overflowing total market value, so one oversized debt book cannot permanently block recovery. [2](#0-1) [23](#0-22) 

### Proof of Concept
1. Through `controller::supply`, create an account and supply `1_000_000_000 * 10^18` base units of an 18-decimal asset to its `(hub_id, asset)` market. [17](#0-16) [24](#0-23) 

2. Supply sufficient collateral in another listed market and call `controller::borrow` for 98% of the oversized market's principal. [25](#0-24) [26](#0-25) 

3. Repeatedly call permissionless `controller::update_indexes(caller, [hub_asset])` as ledger time advances until an accrual chunk panics with `MathOverflow`. [27](#0-26) [28](#0-27) 

4. Attempt `controller::repay` for the borrower and `controller::withdraw` for the supplier; both calls invoke the pool's accrual-first path and revert with `MathOverflow` before debt can be reduced or cash paid out. [29](#0-28) [30](#0-29) [14](#0-13)

### Citations

**File:** common/src/rates/index.rs (L11-19)
```rust
/// Applies `interest_factor` to `old_index` to produce the new borrow index,
/// capped at `MAX_BORROW_INDEX_RAY`.
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
}
```

**File:** common/src/rates/index.rs (L73-86)
```rust
pub fn calculate_supplier_rewards(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    new_borrow_index: Ray,
    old_borrow_index: Ray,
) -> (Ray, Ray) {
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);
```

**File:** contracts/pool/src/interest.rs (L20-32)
```rust
pub(crate) fn global_sync(env: &Env, cache: &mut Cache) {
    if !cache.needs_accrual() {
        return;
    }

    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
    }

    cache.mark_accrued();
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-356)
```rust
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
#[test]
fn a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap() {
    let mut t = LendingTest::new()
        .with_market(big("BIG18", 18, xlm_curve()))
        .with_market(col())
        .with_max_utilization_disabled_all_markets()
        .build();
    lift_caps(&t, "BIG18", 18);
    lift_caps(&t, "COL", 7);
    let principal = BILLION * 10i128.pow(18);
    t.supply_raw(BOB, "BIG18", principal);
    let debt = principal / 100 * 98;
    t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
    t.borrow_raw(ALICE, "BIG18", debt);

    let mut years = 0u32;
    let failure = loop {
        years += 1;
        assert!(
            years <= 40,
            "no cliff within 40 years; the bound in docs/reference/formulas.md is wrong"
        );
        t.advance_time(YEAR_SECS);
        if let Err(e) = t.try_update_indexes_for(&["BIG18"]) {
            break e;
        }
    };
    let failed: Result<(), soroban_sdk::Error> = Err(failure);
    assert_contract_error(failed, errors::MATH_OVERFLOW);
    let last = book(&t, "BIG18");
    assert!(
        last.borrow_index < MAX_BORROW_INDEX_RAY,
        "the index cap did not engage before the value overflow"
    );
    // The market is frozen: exits and repayments accrue first and hit the same panic.
    assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
    assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

**File:** contracts/pool/README.md (L159-167)
```markdown
Each mutation of an existing market runs this sequence:

```text
entrypoint (#[only_owner])
  → Cache::load             # read params + state, bump TTL
  → interest::global_sync   # accrue to now, in ≤1yr chunks
  → mutate                  # cache/shares.rs, cache/cash.rs
  → guards::*               # reserve, utilization, backing checks
  → commit → transfer_out → emit
```

**File:** contracts/pool/src/cache/scale.rs (L19-26)
```rust
    pub(crate) fn calculate_utilization(&self) -> Ray {
        if self.supplied == Ray::ZERO {
            return Ray::ZERO;
        }
        let total_borrowed = scaled_to_original(&self.env, self.borrowed, self.borrow_index);
        let total_supplied = scaled_to_original(&self.env, self.supplied, self.supply_index);

        utilization(&self.env, total_borrowed, total_supplied)
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/scaling.rs (L52-56)
```rust
/// Converts an asset-unit `amount` to a scaled borrow `Ray` using ceiling
/// rounding relative to `borrow_index`.
pub fn calculate_scaled_borrow(env: &Env, amount: i128, decimals: u32, borrow_index: Ray) -> Ray {
    Ray::from_asset(env, amount, decimals).div_ceil(env, borrow_index)
}
```

**File:** contracts/controller/src/external/pool.rs (L54-71)
```rust
pub(crate) fn pool_withdraw_call(
    env: &Env,
    pool_addr: &Address,
    receiver: &Address,
    is_liquidation: bool,
    entries: &Vec<PoolWithdrawEntry>,
) -> Vec<PoolPositionMutation> {
    LiquidityPoolClient::new(env, pool_addr).withdraw(receiver, &is_liquidation, entries)
}

/// Burns debt against prefunded payments and refunds overpayment to `payer`.
pub(crate) fn pool_repay_call(
    env: &Env,
    pool_addr: &Address,
    payer: &Address,
    actions: &Vec<PoolAction>,
) -> Vec<PoolPositionMutation> {
    LiquidityPoolClient::new(env, pool_addr).repay(payer, actions)
```

**File:** contracts/controller/src/external/pool.rs (L109-116)
```rust
/// Accrues and persists market indexes through the current ledger time.
pub(crate) fn pool_update_indexes_call(
    env: &Env,
    pool_addr: &Address,
    hub_assets: &Vec<HubAssetKey>,
) {
    LiquidityPoolClient::new(env, pool_addr).update_indexes(hub_assets)
}
```

**File:** docs/reference/formulas.md (L423-437)
```markdown
| Bound | Consequence |
|---|---|
| Asset decimals 0..=18 | Exact token-to-RAY upscaling. Below 3: collateral only, no flash loans, no liquidation fee, its account's only supply position, at least 2 whole units while in debt |
| Both indexes initially RAY; ceiling 10^36 | 10^9 times initial index; protocol constants |
| Supply-index floor 10^24 | At most 1,000 times the shares minted at index one for the same deposit |
| Borrow APR maximum 2 RAY | 200% annual rate; not a bound on balance growth alone |
| Token-to-RAY input maximum `i128::MAX / 10^(27-d)` | About 170.14 billion whole tokens, before other limits |
| Deposit conversion at the supply-index floor | About 170.14 million whole tokens before scaled-share overflow |

The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
```

**File:** contracts/controller/src/positions/supply.rs (L40-63)
```rust
pub(crate) fn process_supply(
    env: &Env,
    caller: &Address,
    account_id: u64,
    spoke_id: u32,
    assets: &Vec<HubPayment>,
) -> u64 {
    validation::require_authorized_caller(env, caller);
    let aggregated = payments::aggregate_positive_payments(env, assets);
    let mut cache = Context::new(env);

    let (acct_id, mut account) = account::load_or_create_account(
        env,
        caller,
        account_id,
        spoke_id,
        PositionMode::Normal,
        account::AccountGuard::Supply,
        &mut cache,
    );

    require_third_party_existing_supply(env, account_id, acct_id, caller, &account, &aggregated);

    process_deposit(env, caller, &mut account, &aggregated, &mut cache);
```

**File:** contracts/controller/src/positions/supply.rs (L116-132)
```rust
    for (hub_asset, amount_in) in aggregated.iter() {
        let asset_config: AssetConfig = cache.require_spoke_asset(account.spoke_id, &hub_asset);
        let received = payments::transfer_amount_measured(
            env,
            &hub_asset.asset,
            caller,
            &pool_addr,
            amount_in,
            GenericError::AmountMustBePositive,
        );
        let position = account.get_or_create_supply_position(&hub_asset, &asset_config);
        entries.push_back(PoolSupplyEntry {
            action: make_pool_action(&position, received, hub_asset.clone()),
        });
    }

    let results = pool_supply_call(env, &pool_addr, &entries);
```

**File:** contracts/controller/src/positions/supply.rs (L140-157)
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
```

**File:** contracts/controller/src/positions/debt.rs (L33-58)
```rust
pub(crate) fn process_borrow(
    env: &Env,
    caller: &Address,
    account_id: u64,
    borrows: &Vec<HubPayment>,
    to: Option<Address>,
) {
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_positive_payments(env, borrows);

    validate_position_entry_gates(
        env,
        &account,
        &aggregated,
        &mut cache,
        AccountPositionType::Borrow,
    );
    settle_borrow(env, &mut account, &recipient, &aggregated, &mut cache);

```

**File:** contracts/controller/src/positions/debt.rs (L68-81)
```rust
/// Repays with the caller's measured transfers; loads and persists debt only.
pub(crate) fn process_repay(
    env: &Env,
    caller: &Address,
    account_id: u64,
    payments_in: &Vec<HubPayment>,
) {
    validation::require_authorized_caller(env, caller);

    let aggregated = payments::aggregate_positive_payments(env, payments_in);
    let mut account = storage::get_account_borrow_only(env, account_id);
    let mut cache = Context::new(env);

    settle_repay(env, &mut account, caller, &aggregated, &mut cache);
```

**File:** contracts/controller/src/positions/debt.rs (L93-110)
```rust
/// Borrows the aggregated amounts to `recipient` and merges the debt results.
fn settle_borrow(
    env: &Env,
    account: &mut Account,
    recipient: &Address,
    aggregated: &AggregatedPayments,
    cache: &mut Context,
) {
    let pool_addr = cache.cached_pool_address();
    let mut entries: Vec<PoolBorrowEntry> = Vec::new(env);
    for (hub_asset, amount) in aggregated.iter() {
        let position = account.get_or_create_debt_position(&hub_asset);
        entries.push_back(PoolBorrowEntry {
            action: make_pool_action(&position, amount, hub_asset.clone()),
        });
    }
    let results = pool_borrow_call(env, &pool_addr, recipient, &entries);
    for_each_leg(env, &entries, &results, |entry, result| {
```

**File:** contracts/pool/src/ops/repay.rs (L22-32)
```rust
/// Accrues interest, burns the position's debt shares, credits the net repay to cash,
/// commits the market state, and transfers any overpayment back to the payer.
/// The returned mutation's `actual_amount` is the net repay, excluding overpayment.
pub(crate) fn apply(
    env: &Env,
    payer: &Address,
    action: &PoolAction,
) -> (PoolPositionMutation, MarketStateSnapshot) {
    let outcome = accounting(env, action);

    outcome.cache.transfer_out(payer, outcome.overpayment);
```

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }
```
