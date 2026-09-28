### Title
Unchecked interest-accrual value overflow permanently freezes an oversized market - (File: `common/src/rates/simulate.rs`)

### Summary
`accrue_step` converts total scaled debt and supply back to RAY-valued amounts before calculating utilization, and `scaled_to_original` performs a fallible fixed-point multiplication that panics once the represented market value exceeds `i128::MAX`. [1](#0-0) [2](#0-1) 

The public `Controller::update_indexes` path forwards to `LiquidityPool::update_indexes`, where `ops::market::accrue` invokes `global_sync` without recovering from this arithmetic failure. [3](#0-2) [4](#0-3) 

### Finding Description
Every mutating market leg first loads a cache and calls `interest::global_sync`, so repayment, withdrawal, seizure, liquidation, revenue claims, and explicit index synchronization all execute the same accrual code before performing their own accounting. [5](#0-4) [6](#0-5) 

Inside each accrual step, `borrowed * borrow_index / RAY` and `supplied * supply_index / RAY` must fit in `i128`; otherwise the `Ray::mul` call aborts before the protocol’s fixed index caps can make the operation safe. [7](#0-6) [8](#0-7) 

After the crossing point, increasing indexes also make `calculate_supplier_rewards` evaluate `borrowed * new_borrow_index`, creating another overflow site before it can subtract the accrued interest. [9](#0-8) 

Because `last_timestamp` is advanced only after all accrual chunks complete, the failed transaction rolls back the timestamp and every later call repeats the same overflowing calculation. [10](#0-9) 

### Impact Explanation
An unprivileged caller can enter a sufficiently large supported position through `supply` and `borrow`, then any caller can expose the failure with `update_indexes(caller, assets)` after enough ledger time has elapsed. [11](#0-10) [3](#0-2) 

Once crossed, suppliers cannot withdraw, borrowers cannot repay, liquidators cannot seize the affected market, and explicit synchronization keeps reverting, permanently freezing all user funds in that market absent a privileged code upgrade. [12](#0-11) [13](#0-12) [14](#0-13) 

The in-tree reproduction demonstrates a one-billion-token market at 98% utilization reaching this cliff, with `update_indexes`, `withdraw`, and `repay` all returning `MathOverflow` while the borrow index remains below the protocol cap. [15](#0-14) 

### Likelihood Explanation
The scenario requires a very large market and sustained high utilization for multiple years, so it is not trivially reachable on a small deployment. [16](#0-15) 

However, the amounts used are admitted by the configured decimal-domain caps rather than privileged arithmetic or invalid parameters, and a whale or coordinated users can create the necessary utilization without controlling governance. [17](#0-16) [18](#0-17) 

### Recommendation
Do not let market accrual depend on an `i128` conversion that can fail after positions have already been admitted. [19](#0-18) 

Either perform debt/supply valuation and reward accounting in `I256` throughout accrual, or derive and enforce a market-specific index bound from `i128::MAX / scaled_balance` before multiplying, so accrual reaches a safe terminal state instead of reverting forever. [8](#0-7) [20](#0-19) 

Entry checks should also account for future index growth or reject scaled balances that would make the next required valuation unrepresentable; merely capping the index at `MAX_BORROW_INDEX_RAY` is insufficient because the capped product can still overflow. [21](#0-20) 

### Proof of Concept
1. Bob supplies `1_000_000_000 * 10^18` units of an 18-decimal asset by calling `Controller::supply(caller=BOB, account_id=0, spoke_id=S, assets=[(HubAssetKey{hub_id:H,asset:BIG18}, 1_000_000_000 * 10^18)])`. [22](#0-21) 

2. Alice supplies sufficient collateral, then calls `Controller::borrow(caller=ALICE, account_id=A, borrows=[(HubAssetKey{hub_id:H,asset:BIG18}, 980_000_000 * 10^18)], to=Some(ALICE))`, establishing approximately 98% utilization. [23](#0-22) 

3. Leave the market untouched while ledger time advances under a high-utilization interest curve, then call `Controller::update_indexes(caller=ANY, assets=[HubAssetKey{hub_id:H,asset:BIG18}])`; the call enters `pool.update_indexes`, whose `accrue_step` panics while unscaling total debt or supply. [24](#0-23) [25](#0-24) [26](#0-25) 

4. Subsequent `withdraw`, `repay`, liquidation, `clean_bad_debt`, `claim_revenue`, and further `update_indexes` calls touching that market all reach the same mandatory accrual and revert with `MathOverflow`, as demonstrated by the checked-in reproduction. [27](#0-26) [28](#0-27)

### Citations

**File:** common/src/rates/simulate.rs (L60-71)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);

    let new_supply_index = update_supply_index(env, supplied, supply_index, supplier_rewards);
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** contracts/controller/src/lib.rs (L90-115)
```rust
    /// Supplies `assets` as collateral and returns the account id; `account_id = 0`
    /// creates an account in `spoke_id`. Third parties may only top up existing
    /// supply positions; owners and delegates may add assets.
    #[when_not_paused]
    fn supply(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        assets: Vec<(HubAssetKey, i128)>,
    ) -> u64 {
        positions::process_supply(&env, &caller, account_id, spoke_id, &assets)
    }

    /// Borrows against `account_id`'s collateral, paying `to` or the caller.
    /// Requires owner or delegate authorization and post-borrow solvency.
    #[when_not_paused]
    fn borrow(
        env: Env,
        caller: Address,
        account_id: u64,
        borrows: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) {
        positions::process_borrow(&env, &caller, account_id, &borrows, to);
    }
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

**File:** contracts/pool/src/ops/mod.rs (L29-47)
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

**File:** common/src/rates/index.rs (L80-86)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);
```

**File:** contracts/pool/src/interest.rs (L25-32)
```rust
    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
    }

    cache.mark_accrued();
```

**File:** contracts/pool/src/ops/withdraw.rs (L57-64)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

```

**File:** contracts/pool/src/ops/repay.rs (L36-44)
```rust
/// Accrues interest, resolves the repay amount into burned debt shares and
/// overpayment, burns the shares, and credits the net repay to cash without
/// transferring the overpayment refund. Panics if a positive net repay would
/// burn zero scaled shares.
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
```

**File:** contracts/pool/src/ops/seize.rs (L14-21)
```rust
/// Applies one seize entry, syncing the market, socializing bad debt or
/// reclassifying supply as revenue depending on `entry.side`, and returns the
/// committed market snapshot. Does not transfer tokens; the controller adjusts
/// the position books. Panics if `entry.position.scaled_amount` is negative.
pub(crate) fn apply(env: &Env, entry: &PoolSeizeEntry) -> MarketStateSnapshot {
    require_nonneg_amount(env, entry.position.scaled_amount);
    let mut cache = ops::synced_market(env, &entry.hub_asset);
    let position = Ray::from(entry.position.scaled_amount);
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L81-95)
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
}
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

**File:** docs/reference/formulas.md (L425-437)
```markdown
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
