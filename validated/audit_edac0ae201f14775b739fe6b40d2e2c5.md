### Title
Unbounded accrued market value overflows `i128` and permanently freezes market operations - (File: common/src/rates/scaling.rs)

### Summary

A sufficiently large market at sustained high utilization can make the accrued borrow value exceed the `i128`-backed RAY domain before the borrow-index ceiling is reached. Because every pool mutation synchronizes interest before applying the requested operation, the resulting `MathOverflow` permanently blocks repayment, withdrawal, liquidation, and manual index updates for that market. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description

`Controller::update_indexes`, `withdraw`, `repay`, `borrow`, `liquidate`, and `clean_bad_debt` all ultimately reach pool paths that load a market through `synced_market`. That helper always calls `interest::global_sync` before the requested action is applied. [4](#0-3) [5](#0-4) 

`global_sync` invokes `accrue_step` for each elapsed accrual chunk, while debt value conversion uses `scaled_to_original`, which multiplies scaled debt by the borrow index. [6](#0-5) [7](#0-6) 

The protocol caps the borrow index itself, but it does not cap the product `scaled_debt × borrow_index` to the finite `i128` RAY range. A repository integration test demonstrates this exact sequence: a roughly 98%-utilized 18-decimal market eventually makes `update_indexes` fail with `MathOverflow`, after which both `withdraw` and `repay` fail with the same error before their requested logic executes. [3](#0-2) [8](#0-7) 

Once the accrual calculation overflows, advancing to a later timestamp does not recover the market because every subsequent synchronization attempts to accrue an even larger value. [6](#0-5) [9](#0-8) 

### Impact Explanation

The affected market permanently loses the ability to process repayments, withdrawals, liquidations, bad-debt cleanup, and index updates under the deployed arithmetic. Suppliers cannot access their underlying tokens and borrowers cannot close debt, so this constitutes permanent freezing of user funds rather than a transient failed transaction. [10](#0-9) [11](#0-10) 

The freeze can also leave bad debt unliquidatable and prevent ordinary recovery through permissionless `recapitalize`, since that controller path still invokes a pool operation on the affected market after measuring the receipt. [12](#0-11) 

### Likelihood Explanation

The trigger requires an extremely large book and sustained high utilization for enough time to approach the RAY value ceiling; it is not reachable on a small or conservatively capped market. The required setup is nevertheless submitted entirely through unprivileged `supply`, `borrow`, and later `update_indexes` calls when the configured caps and available token supply permit the position. [13](#0-12) [14](#0-13) [15](#0-14) 

The project documentation explicitly recognizes that valid caps and bounded indexes do not guarantee future accrual fits the RAY domain, and that value overflow can block repayment and withdrawal before the index ceiling. [8](#0-7) 

### Recommendation

Track accrued market values in a wider type such as `I256`, or preflight each accrual chunk so `scaled_debt × next_borrow_index` cannot exceed the `i128` RAY domain. Enforce market caps based on the maximum future accrued value, not only current token units, and make the configured index ceiling engage strictly before the value-product ceiling. Add a recovery-safe path that can stop further growth or settle positions without requiring the already-overflowing global accrual to succeed.

### Proof of Concept

1. For a market admitted with sufficient caps, an attacker calls `supply(caller, account_id, spoke_id, [(hub_asset, principal)])` with a very large `principal`.
2. The attacker supplies collateral in another listed market and calls `borrow(caller, account_id, [(hub_asset, debt)], to)` to bring the target market to sustained high utilization.
3. After enough ledger time passes, anyone calls `update_indexes(caller, [hub_asset])`.
4. `update_indexes` loads the market through `synced_market`, which calls `global_sync`; the accrued scaled-debt product overflows `i128` and returns `MathOverflow`.
5. Subsequent `repay`, `withdraw`, `liquidate`, and `clean_bad_debt` calls also enter the same accrual path and revert before repayment, withdrawal, or seizure logic executes. [4](#0-3) [16](#0-15)

### Citations

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

**File:** contracts/controller/src/lib.rs (L367-394)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }

    /// Claims pool revenue and forwards measured receipts to the accumulator.
    /// Returns those amounts in asset units, in input order. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn claim_revenue(env: Env, caller: Address, assets: Vec<HubAssetKey>) -> Vec<i128> {
        markets::claim_revenue(&env, caller, assets)
    }

    /// Refreshes supply LTV snapshots. With `has_risks`, also refreshes gated
    /// liquidation parameters and requires a final health factor of at least
    /// 1.05 WAD. Permissionless; requires caller authorization.
    #[when_not_paused]
    fn update_account_threshold(env: Env, caller: Address, has_risks: bool, account_ids: Vec<u64>) {
        risk::params::update_account_threshold(&env, caller, has_risks, account_ids);
    }

    /// Covers a pool backing shortfall using measured receipts from `payer`.
    /// Refunds excess and returns the amount applied in asset units.
    /// Permissionless; requires payer authorization.
    fn recapitalize(env: Env, payer: Address, hub_asset: HubAssetKey, amount: i128) -> i128 {
        markets::recapitalize(&env, payer, hub_asset, amount)
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** docs/reference/formulas.md (L432-437)
```markdown
The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
```

**File:** contracts/controller/src/markets.rs (L140-164)
```rust
/// Transfers funds to the pool, credits the measured receipt up to the backing
/// shortfall, and refunds unused funds. Returns credited cash; rejects flash loans.
pub(crate) fn recapitalize(
    env: &Env,
    payer: Address,
    hub_asset: HubAssetKey,
    amount: i128,
) -> i128 {
    validation::require_authorized_caller(env, &payer);
    require_positive_amount(env, amount);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    // Prefund the pool and credit only its measured receipt.
    let received = payments::transfer_amount_measured(
        env,
        &hub_asset.asset,
        &payer,
        &pool_addr,
        amount,
        GenericError::AmountMustBePositive,
    );

    pool_recapitalize_call(env, &pool_addr, &hub_asset, &payer, received).actual_amount
}
```
