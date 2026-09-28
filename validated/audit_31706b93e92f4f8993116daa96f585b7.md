### Title
Integer overflow during interest accrual permanently freezes oversized high-utilization markets - (File: contracts/pool/src/interest.rs)

### Summary
The pool’s RAY-scaled debt calculation can overflow `i128` before the borrow-index ceiling is reached, causing every subsequent market operation that performs interest accrual to revert and leaving supplier and borrower funds frozen. [1](#0-0) [2](#0-1) 

### Finding Description
Interest accrual computes aggregate debt as `borrowed * borrow_index`, where both values are represented in the RAY domain and the resulting scaled value must fit in `i128`. [3](#0-2) [4](#0-3) 

For a sufficiently large market, the borrow index can grow to a value for which `borrowed * borrow_index / RAY` exceeds `i128::MAX` while still remaining below `MAX_BORROW_INDEX_RAY`. [5](#0-4) [6](#0-5) 

`global_sync` panics inside the accrual step before `cache.mark_accrued()` or `cache.commit()` executes, so `last_timestamp` remains behind and every later call retries the same overflowing calculation. [7](#0-6) [8](#0-7) 

All ordinary pool legs load an interest-synced market through `synced_market` or `load_leg`, meaning supply, borrow, withdraw, repay, liquidation settlement, and related mutations all hit the same overflow before their own logic runs. [9](#0-8) [10](#0-9) 

An unprivileged user can reach the condition through controller `supply` and `borrow` operations that create a large scaled book at sustained high utilization, and can then invoke `update_indexes` with the affected `HubAssetKey` once enough ledger time has elapsed. [11](#0-10) [12](#0-11) 

The repository’s own integration test constructs a one-billion-token, 18-decimal market at 98% utilization, advances accrual until `MathOverflow`, and confirms that subsequent withdrawal and repayment attempts fail for the same reason. [13](#0-12) 

### Impact Explanation
This is a permanent freezing-of-funds condition for the affected market: suppliers cannot withdraw, borrowers cannot repay, liquidations cannot settle the market, and direct index updates cannot advance state. [2](#0-1) 

The pool’s own administrative `update_params` path also accrues interest before installing a new rate model, so changing interest parameters does not provide an in-protocol recovery path once the overflow state is reached. [14](#0-13) 

Because every retry fails before committing a new accrual timestamp, the market remains stuck at the last successful timestamp rather than recovering after one failed transaction. [7](#0-6) 

### Likelihood Explanation
Triggering the cliff requires a market whose RAY-scaled position is large enough that index growth crosses the representable aggregate-value bound before the configured index ceiling is reached. [15](#0-14) 

An attacker does not need privileged access, but does need either an existing large market to push into sustained high utilization or enough collateral and liquidity to create the state through ordinary `supply`, `borrow`, and later `update_indexes` calls. [16](#0-15) 

The practical likelihood is medium: the transaction path is permissionless and deterministic, while the capital requirements, configured caps, utilization limits, and time-dependent accrual restrict when it can be achieved. [17](#0-16) [18](#0-17) 

### Recommendation
- Perform aggregate accrual calculations in `I256`, or explicitly cap `borrow_index` and `supply_index` at the largest values for which `borrowed * index / RAY` and `supplied * index / RAY` remain representable. [19](#0-18) [3](#0-2) 
- Reject new supply or borrow when the resulting scaled totals could overflow at the configured index ceiling, rather than relying only on native-amount caps. [15](#0-14) 
- If the safe index bound is reached, commit a terminal “interest stopped” state that still permits repayment, withdrawal, liquidation, and recapitalization instead of reverting during accrual. [7](#0-6) 
- Add regression coverage around `MathOverflow` inside `accrue_step`, including proof that a market remains operable after reaching the safe aggregate-value bound. [20](#0-19) 

### Proof of Concept
1. Configure or select an 18-decimal market whose admitted cap permits approximately `1_000_000_000 * 10^18` base units of supply. [21](#0-20) 
2. Through controller `supply`, populate the market with that amount using `assets = [(HubAssetKey { hub_id, asset }, amount)]`. [22](#0-21) 
3. Through controller `borrow`, borrow approximately 98% of the market cash using `borrows = [(HubAssetKey { hub_id, asset }, debt)]` and a receiver controlled by the caller. [23](#0-22) 
4. Maintain the high-utilization borrow position while ledger time advances, then call controller `update_indexes` with `hub_assets = [HubAssetKey { hub_id, asset }]`. [8](#0-7) 
5. Accrual panics with `MathOverflow` before committing `last_timestamp`; subsequent `update_indexes`, `withdraw`, and `repay` transactions repeat the same overflowing accrual and revert. [24](#0-23)

### Citations

**File:** common/src/rates/index.rs (L11-18)
```rust
/// Applies `interest_factor` to `old_index` to produce the new borrow index,
/// capped at `MAX_BORROW_INDEX_RAY`.
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L73-88)
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

    (supplier_rewards, protocol_fee)
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

**File:** docs/reference/formulas.md (L20-24)
```markdown
Protocol boundaries require non-negative amounts; `Ray`, `Wad` and `Bps`
constructors do not enforce that restriction themselves. Multiply-divide uses
an `i128` fast path or an exact `I256` intermediate. Unrepresentable results
raise `MathOverflow`, except at explicit saturating sites; zero divisors raise
`DivisionByZero`.
```

**File:** docs/reference/formulas.md (L407-417)
```markdown
A cap is in native token units. Entry compares stored scaled usage plus the
new scaled amount with the cap floor-converted at the current index. Zero cap
allows no positive exposure. Exits subtract usage without checking caps;
missing usage rows and zero exit deltas are no-ops. Cap→scaled conversion
saturates at `i128::MAX` (`calculate_scaled_cap`), so the entry check fails
open instead of trapping. A saturated scaled cap does not enforce the
configured asset-unit limit. An admitted cap saturates only at an index below
one RAY. Only a bad-debt write-down moves the supply index below one RAY; at
its floor (`RAY / 1000`), a supply cap above 1/1000 of the admitted maximum
saturates. The borrow index never falls below one RAY, so an admitted borrow
cap cannot saturate. Position conversion still rejects overflow.
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

**File:** contracts/pool/src/interest.rs (L20-33)
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
}
```

**File:** contracts/pool/src/ops/market.rs (L50-57)
```rust
/// Accrues interest under the old model, commits it, then replaces the interest
/// and flash-loan parameters and validates them against the stored decimals.
pub(crate) fn replace_rate_model(env: &Env, hub_asset: HubAssetKey, model: InterestRateModel) {
    ops::renewed_market(env, &hub_asset).commit();

    let params = storage::write_rate_model(env, &hub_asset, &model);
    params.verify(env);
    events::emit_market_params(env, hub_asset.hub_id, hub_asset.asset, params);
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

**File:** contracts/pool/src/lib.rs (L128-180)
```rust
    /// Accrues, mints scaled supply shares and credits cash per entry. The
    /// controller transfers the tokens in before this call. Owner-only.
    #[only_owner]
    fn supply(env: Env, entries: Vec<PoolSupplyEntry>) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, ops::supply::apply)
    }

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
    }

    /// Burns supply shares and transfers the underlying to `receiver`.
    /// `is_liquidation` skips the max-utilization check and may withhold a
    /// protocol fee. Owner-only; `actual_amount` is gross of that fee.
    #[only_owner]
    fn withdraw(
        env: Env,
        receiver: Address,
        is_liquidation: bool,
        entries: Vec<PoolWithdrawEntry>,
    ) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, |env, entry| {
            ops::withdraw::apply(env, &receiver, is_liquidation, entry)
        })
    }

    /// Burns scaled debt up to the repay amount, credits cash with the net
    /// repay and refunds overpayment to `payer`. Owner-only.
    #[only_owner]
    fn repay(env: Env, payer: Address, actions: Vec<PoolAction>) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, actions, |env, action| {
            ops::repay::apply(env, &payer, action)
        })
    }

    /// Accrues interest for each market in `hub_assets` through the current
    /// ledger time. Commits state even with no elapsed time to reserve the write
    /// footprint, and emits its market state event. Restricted to the owner.
    #[only_owner]
    fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>) {
        ops::market::accrue(&env, hub_assets);
    }
```

**File:** contracts/controller/src/external/pool.rs (L20-38)
```rust
/// Credits prefunded deposits and returns updated scaled positions and indexes.
/// The controller must transfer and measure receipts before this call.
pub(crate) fn pool_supply_call(
    env: &Env,
    pool_addr: &Address,
    entries: &Vec<PoolSupplyEntry>,
) -> Vec<PoolPositionMutation> {
    LiquidityPoolClient::new(env, pool_addr).supply(entries)
}

/// Mints scaled debt and transfers borrowed assets to `receiver`.
pub(crate) fn pool_borrow_call(
    env: &Env,
    pool_addr: &Address,
    receiver: &Address,
    entries: &Vec<PoolBorrowEntry>,
) -> Vec<PoolPositionMutation> {
    LiquidityPoolClient::new(env, pool_addr).borrow(receiver, entries)
}
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

**File:** common/src/math/fp_core.rs (L14-29)
```rust
/// Widens `x`, `y`, and `d` to `I256` for overflow-safe intermediate arithmetic.
fn to_i256_operands(env: &Env, x: i128, y: i128, d: i128) -> (I256, I256, I256) {
    (
        I256::from_i128(env, x),
        I256::from_i128(env, y),
        I256::from_i128(env, d),
    )
}

/// Panics with `GenericError::DivisionByZero` if `d` is zero. Every panicking
/// multiply-divide calls this first so a zero denominator surfaces as a
/// protocol error rather than as an untyped host arithmetic trap.
fn require_nonzero_divisor(env: &Env, d: i128) {
    if d == 0 {
        panic_with_error!(env, GenericError::DivisionByZero);
    }
```
