### Title
Permanent market freeze from unchecked index-scaled debt multiplication - (File: `common/src/rates/simulate.rs`)

### Summary
High. A very large market can reach a state where ordinary interest accrual overflows `i128` while converting scaled debt to its RAY value. Because every pool mutation synchronizes interest before accounting, subsequent `update_indexes`, `withdraw`, `repay`, borrow-side liquidations, and other market operations revert indefinitely. The configured `MAX_BORROW_INDEX_RAY` ceiling does not prevent the overflow because the debt-value multiplication occurs before the index cap can become a safe stopping condition.

### Finding Description
`accrue_step` starts by evaluating `scaled_to_original(borrowed, borrow_index)` and `scaled_to_original(supplied, supply_index)`. [1](#0-0)  `scaled_to_original` performs a checked fixed-point multiplication, so an aggregate scaled balance multiplied by a sufficiently grown index panics with `MathOverflow`. [2](#0-1) 

The borrow index is nominally capped at `MAX_BORROW_INDEX_RAY`, but that cap is applied only when updating the index after utilization has already been calculated. [3](#0-2)  `MAX_BORROW_INDEX_RAY` is `1e36` raw RAY, while an `i128` can represent only about `1.70e38`; consequently, a scaled balance above roughly `170` forces `borrowed * MAX_BORROW_INDEX_RAY` outside `i128`, and the same overflow can occur earlier. [4](#0-3) 

Every market operation loads the market through `synced_market`, which calls `interest::global_sync` before the operation-specific logic. [5](#0-4)  `global_sync` invokes `accrue_step` for each elapsed chunk, so any elapsed time after the unsafe balance/index combination is reached repeats the overflow. [6](#0-5)  The permissionless controller `update_indexes` path forwards to the same pool accrual path. [7](#0-6) 

The repository already contains a reproduction in which a one-billion-token, 18-decimal market at 98% utilization eventually overflows during `update_indexes`; the test then confirms that both supplier withdrawal and borrower repayment fail with `MathOverflow`. [8](#0-7) 

### Impact Explanation
This permanently freezes all funds and obligations in the affected `(hub_id, asset)` market absent a contract upgrade. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot retire debt, and maintenance calls cannot accrue the market because all of those paths synchronize the same overflowing market state first. [9](#0-8)  Withdrawal explicitly loads an interest-synced cache before resolving or burning shares. [10](#0-9)  Repayment does the same before resolving debt or crediting cash. [11](#0-10) 

The failure is not a normal liquidity limit: the pool can still physically hold supplier cash, but the accounting entrypoint cannot execute. Even a governance attempt to replace the interest-rate model accrues under the old model first and therefore also reverts. [12](#0-11) 

### Likelihood Explanation
The attack requires an unusually large market and sustained debt, so it is capital-intensive rather than a low-cost griefing vector. A single unprivileged address can nevertheless create the state by supplying the large asset position and sufficient collateral, borrowing at high utilization, and waiting for interest accrual. The repository's proof scenario uses governance-allowed maximum decimal-domain caps rather than privileged pool mutation. [13](#0-12) 

The likelihood is higher for high-decimal assets or steep high-utilization curves because raw token amounts translate into large RAY-scaled balances. The deterministic test demonstrates the cliff before the configured borrow-index ceiling is reached and confirms that exits and repayments subsequently revert. [14](#0-13) 

### Recommendation
Enforce a representability invariant on aggregate scaled balances before accepting new supply or debt. In particular, ensure:

- `supplied <= i128::MAX / MAX_SUPPLY_INDEX_RAY`
- `borrowed <= i128::MAX / MAX_BORROW_INDEX_RAY`

Apply the bound in the pool's share-mint paths rather than only in per-spoke caps, because multiple spokes share the same physical market totals. Alternatively, calculate utilization and aggregate debt/supply values with `I256` or another representation that cannot overflow before index capping. Add a regression test based on the existing whale-market cliff showing that accrual reaches the index cap or rejects further growth instead of permanently freezing `withdraw`, `repay`, `liquidate`, and `update_indexes`.

### Proof of Concept
The existing test establishes the setup and failure. It configures an 18-decimal `BIG18` market with a steep rate curve, lifts the tested caps to their decimal-domain maximum, supplies `1_000_000_000 * 10^18` raw units, and borrows 98% of that amount against collateral. [15](#0-14) 

A single caller can execute the same shape:

```rust
let big = HubAssetKey { hub_id, asset: big18 };
let col = HubAssetKey { hub_id, asset: col };

let account_id = controller.supply(
    caller,
    0,
    spoke_id,
    vec![&env, (big.clone(), 1_000_000_000 * 10i128.pow(18))],
);

controller.supply(
    caller,
    account_id,
    spoke_id,
    vec![&env, (col, 30_000_000_000_000_000 * 10i128.pow(7))],
);

controller.borrow(
    caller,
    account_id,
    vec![&env, (big.clone(), 980_000_000 * 10i128.pow(18))],
    None,
);

// After enough ledger time has elapsed:
controller.update_indexes(caller, vec![&env, big]);
```

The final call reaches `Controller::update_indexes`, whose pool call invokes `ops::market::accrue`, `Cache::load`, `global_sync`, and `accrue_step`. [7](#0-6) [16](#0-15)  The checked multiplication at `scaled_to_original` then raises `MathOverflow`, leaving the market below `MAX_BORROW_INDEX_RAY` but unable to process later accrual, withdrawals, or repayments. [17](#0-16)

### Citations

**File:** common/src/rates/simulate.rs (L51-63)
```rust
pub fn accrue_step(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    supplied: Ray,
    borrow_index: Ray,
    supply_index: Ray,
    delta_ms: u64,
) -> AccrualStep {
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** contracts/pool/src/ops/mod.rs (L29-46)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
}

/// Renews instance TTL, then loads and accrues the market.
pub(crate) fn renewed_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    renew_instance(env);
    synced_market(env, hub_asset)
}

/// Validates `action.amount ≥ 0`, syncs the market, and returns (cache, scaled position).
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
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

**File:** contracts/controller/src/markets.rs (L89-100)
```rust
pub(crate) fn upgrade_liquidity_pool_params(
    env: &Env,
    hub_asset: &HubAssetKey,
    params: &InterestRateModel,
) {
    let mut cache = Context::new(env);

    let pool_addr = cache.cached_pool_address();

    pool_update_indexes_call(env, &pool_addr, &vec![env, hub_asset.clone()]);

    pool_update_params_call(env, &pool_addr, hub_asset, params);
```

**File:** contracts/controller/src/markets.rs (L118-125)
```rust
/// Accrues indexes for each hub asset. Requires caller authorization and no flash loan.
pub(crate) fn update_indexes(env: &Env, caller: Address, assets: Vec<HubAssetKey>) {
    validation::require_authorized_caller(env, &caller);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    pool_update_indexes_call(env, &pool_addr, &assets);
}
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L81-94)
```rust
fn lift_caps(t: &LendingTest, asset: &str, decimals: u32) {
    let cap = max_cap_for_decimals(decimals);
    let cfg = t.get_asset_config(asset);
    t.edit_asset_in_spoke_caps(
        asset,
        HARNESS_SPOKE,
        true,
        true,
        cfg.loan_to_value,
        cfg.liquidation_threshold,
        cfg.liquidation_bonus,
        cap,
        cap,
    );
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-356)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
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

**File:** contracts/pool/src/ops/withdraw.rs (L57-65)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
```

**File:** contracts/pool/src/ops/repay.rs (L36-45)
```rust
/// Accrues interest, resolves the repay amount into burned debt shares and
/// overpayment, burns the shares, and credits the net repay to cash without
/// transferring the overpayment refund. Panics if a positive net repay would
/// burn zero scaled shares.
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
```

**File:** contracts/pool/src/ops/market.rs (L65-72)
```rust
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
    }
```
