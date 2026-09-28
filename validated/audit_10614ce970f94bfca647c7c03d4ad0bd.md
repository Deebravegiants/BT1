### Title
RAY-valued debt overflow during accrual permanently freezes a large market - (File: common/src/rates/scaling.rs)

### Summary
A sufficiently large market at sustained high utilization can make `borrowed_scaled * borrow_index / RAY` exceed `i128::MAX` before `MAX_BORROW_INDEX_RAY` is reached. Interest accrual then panics inside `scaled_to_original`, and because every monetary pool leg syncs the market before executing, subsequent withdrawals, repayments, liquidations, and index updates revert. [1](#0-0) [2](#0-1) 

### Finding Description
`Controller::update_indexes` is permissionless and forwards the selected `Vec<HubAssetKey>` to the market accrual path. [3](#0-2)  The pool’s `update_indexes` invokes `ops::market::accrue`, while `global_sync` applies each accrual chunk through `accrue_step`. [4](#0-3) [5](#0-4)  The rate calculation derives utilization by unscaling aggregate debt and supply through `scaled_to_original`; that multiplication panics when the RAY-valued result leaves `i128`. [6](#0-5) [2](#0-1) 

The vulnerable ordering is that the value overflow can occur while `borrow_index` remains below its configured ceiling, so the ceiling does not stop accrual before the panic. [7](#0-6)  Withdraw and repay both call `ops::load_leg`, which loads a synced cache and therefore executes the failing accrual before either operation can resolve or burn shares. [8](#0-7) [9](#0-8) [10](#0-9) 

### Impact Explanation
This permanently freezes all supplier funds and blocks repayment or liquidation in the affected `(hub, token)` market. [11](#0-10)  Ledger time cannot move backward, so the same multiplication remains out of range on every later accrual attempt. [5](#0-4)  The checked-in reproduction explicitly demonstrates `MathOverflow` from `update_indexes`, followed by the same failure for a one-unit withdrawal and a repayment. [12](#0-11) 

### Likelihood Explanation
An unprivileged account can establish the prerequisite state through ordinary supply collateralization and borrowing, provided the market’s configured caps, available liquidity, collateral, and rate model admit a RAY-valued debt position near the numeric boundary. [13](#0-12)  This requires a very large position and sustained accrual, so the practical likelihood is lower than an ordinary accounting error, but no privileged action is required once such a market configuration exists. [14](#0-13)  The impact is High because victim deposits become permanently inaccessible rather than merely temporarily delayed. [11](#0-10) 

### Recommendation
Perform aggregate index unscaling in a wider integer type such as `U256`, or add a checked domain guard that keeps `borrowed_scaled * borrow_index / RAY` and `supplied_scaled * supply_index / RAY` representable before calculating utilization. Apply the borrow-index ceiling before any operation that can overflow total-debt valuation, and make accrual at the ceiling a deterministic no-op rather than an arithmetic panic. Add the checked-in cliff scenario as a regression test against every market-mutating entrypoint. [6](#0-5) [15](#0-14) 

### Proof of Concept
The checked-in test creates an 18-decimal market, supplies `1_000_000_000 * 10^18` units, borrows 98% of it, and repeatedly calls `update_indexes`; the call fails with `MathOverflow` while the borrow index is still below `MAX_BORROW_INDEX_RAY`, after which withdrawal and repayment also fail. [16](#0-15) 

Equivalent single-address flow:

```rust
let market = HubAssetKey { hub_id, asset_id: big18_asset };
let supplied = 1_000_000_000i128 * 10i128.pow(18);
let borrowed = supplied / 100 * 98;

// Fund the debt market and provide sufficient separate collateral.
controller.supply(
    attacker,
    0,
    spoke_id,
    (market.clone(), supplied),
);

// Borrow up to the risk and liquidity limit.
controller.borrow(
    attacker,
    account_id,
    (market.clone(), borrowed),
    None,
);

// Permissionless accrual eventually crosses the RAY-value ceiling.
controller.update_indexes(
    attacker,
    vec![env, market.clone()],
);

// These now revert during the same mandatory accrual.
controller.withdraw(supplier, supplier_account_id, (market.clone(), 1));
controller.repay(attacker, account_id, (market, 1));
```

### Citations

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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** contracts/pool/src/lib.rs (L174-179)
```rust
    /// Accrues interest for each market in `hub_assets` through the current
    /// ledger time. Commits state even with no elapsed time to reserve the write
    /// footprint, and emits its market state event. Restricted to the owner.
    #[only_owner]
    fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>) {
        ops::market::accrue(&env, hub_assets);
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

**File:** contracts/pool/src/ops/mod.rs (L42-46)
```rust
/// Validates `action.amount ≥ 0`, syncs the market, and returns (cache, scaled position).
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
```

**File:** contracts/pool/src/ops/withdraw.rs (L62-65)
```rust
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
```

**File:** contracts/pool/src/ops/repay.rs (L40-44)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
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
