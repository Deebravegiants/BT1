### Title
Accrual arithmetic overflow permanently freezes oversized markets - (File: `common/src/rates/simulate.rs`) [1](#0-0) 

### Summary
A market whose scaled supply or debt is large enough that `scaled * index` no longer fits in `i128` permanently bricks that market before the configured index ceiling can engage. Every later accrual, repayment, withdrawal, and liquidation reverts with `MathOverflow`, permanently freezing supplier funds in the affected market.

### Finding Description
`accrue_step` computes aggregate debt and supply by calling `scaled_to_original`, which evaluates `scaled.mul(index)` and requires the resulting RAY value to fit `i128`. [1](#0-0) [2](#0-1) 

This multiplication occurs before `update_borrow_index` can clamp the newly calculated index to `MAX_BORROW_INDEX_RAY`. [3](#0-2) 

The public `update_indexes` entrypoint is permissionless and calls the pool accrual path, while `withdraw`, `repay`, `borrow`, supply, liquidation settlement, and other position mutations all load the market through `ops::load_leg` → `synced_market` → `interest::global_sync`. [4](#0-3) [5](#0-4) 

For an 18-decimal asset, one billion whole tokens corresponds to `1e36` scaled RAY at index `RAY`; once the borrow index exceeds roughly `173.6 * RAY`, the stored debt aggregate overflows `i128`. [6](#0-5) 

The repository's regression test demonstrates this exact cliff: an admitted billion-token market at 98% utilization eventually fails inside accrual with `MathOverflow`, while the borrow index remains below `MAX_BORROW_INDEX_RAY`, and subsequent withdrawals and repayments fail identically. [7](#0-6) 

### Impact Explanation
This is a permanent freezing of all supplier funds and unclaimed yield in the affected `(hub, asset)` book. Borrowers cannot repay or close positions, suppliers cannot withdraw, liquidators cannot resolve unhealthy positions, and even the permissionless `update_indexes` path cannot advance state. [8](#0-7) [9](#0-8) 

Because the panic occurs before a new index or timestamp is committed, repeated calls cannot skip the failing interval or recover the market. [10](#0-9) 

### Likelihood Explanation
The trigger requires an unusually large but protocol-representable market, high utilization, and sufficient elapsed interest for the index to cross the aggregate-value limit. The documented admission domain is approximately 170 billion whole tokens, but individual market caps can admit less, so exploitability depends on a listed asset's cap, decimals, collateral value, and rate curve. [11](#0-10) 

A single unprivileged caller can create the state with `supply(caller, 0, spoke_id, [(collateral, collateral_amount), (target, target_amount)])`, then `borrow(caller, account_id, [(target, borrow_amount)], None)`, subject to ordinary liquidity and solvency checks. [12](#0-11) 

After the position exists, anyone can trigger the freeze through `update_indexes(caller, [target])` once enough time has elapsed. [13](#0-12) 

The substantial capital and time requirements make this a Medium-severity availability failure rather than an immediate theft primitive.

### Recommendation
Prevent stored scaled aggregates from ever reaching an index at which `scaled * index / RAY` cannot be represented:

- Enforce a dynamic index ceiling, `floor(i128::MAX * RAY / max(supplied_scaled, borrowed_scaled))`, before performing `scaled_to_original`.
- When an index reaches that ceiling, treat the market as interest-capped instead of panicking, so repay, withdraw, liquidation, and bad-debt cleanup remain operational.
- Alternatively, perform aggregate valuation and accrued-interest calculations in `I256`, but store only values that remain representable and define explicit saturation behavior.
- Reduce admitted supply/borrow caps where governance does not intend to redesign accrual arithmetic.
- Add a boundary test proving that `withdraw`, `repay`, `liquidate`, and `update_indexes` remain callable at the index ceiling.

### Proof of Concept
For a valid 18-decimal target asset `A` and collateral asset `C`:

1. Call `supply(attacker, 0, spoke_id, [(C, collateral_amount), (A, 1_000_000_000e18)])` to create an account and a `1e36`-scaled target market.
2. Call `borrow(attacker, account_id, [(A, 980_000_000e18)], None)` to establish approximately 98% utilization while remaining solvent.
3. Allow the high-utilization market to accrue until its index approaches the aggregate-value limit.
4. Call `update_indexes(attacker, [A])`.
5. `accrue_step` panics at `scaled_to_original(borrowed, borrow_index)` or `scaled_to_original(supplied, supply_index)` with `MathOverflow`.
6. Subsequent `repay`, `withdraw`, `liquidate`, and `update_indexes` calls all reach accrual first and fail with the same error. [14](#0-13)

### Citations

**File:** common/src/rates/simulate.rs (L51-61)
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
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

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

**File:** contracts/pool/src/ops/repay.rs (L40-55)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    assert_with_error!(
        env,
        net_repay == 0 || burned.raw() > 0,
        GenericError::RepayRoundsToZeroShares
    );

    let position = position.checked_sub(env, burned);
    cache.burn_debt(burned);
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

**File:** docs/reference/formulas.md (L423-435)
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
