### Title
Sustained high-utilization accrual permanently freezes a large market through RAY-value overflow - (File: contracts/pool/src/interest.rs)

### Summary
A market can cross the `i128` representable limit for `borrowed × borrow_index` before the configured `MAX_BORROW_INDEX_RAY` is reached. When that happens, `global_sync` panics while accruing; because the timestamp is not advanced and every withdrawal, repayment, liquidation, or later accrual synchronizes first, the market becomes permanently unusable. [1](#0-0) [2](#0-1) 

### Finding Description
`global_sync` repeatedly calls `accrue_chunk`, which delegates index and reward computation to `accrue_step`. [3](#0-2)  `calculate_supplier_rewards` computes both `borrowed.mul(old_borrow_index)` and `borrowed.mul(new_borrow_index)` before subtracting accrued interest. [2](#0-1)  `Ray::mul` returns an `i128` result, so a market whose scaled debt and index product exceeds `i128::MAX` raises `MathOverflow`. [4](#0-3) 

The borrow-index cap does not prevent this state: it only clamps the index to `10^9×`, while the scaled-debt product can overflow at a much lower index when the underlying market is large enough. [5](#0-4) [6](#0-5)  Caps only ensure that the initial token amount can be represented after RAY scaling; they do not bound the later `scaled_amount × index` product. [7](#0-6) 

Every normal pool leg calls `synced_market`, which loads the market and calls `global_sync` before the requested mutation. [8](#0-7)  Repayment calls `load_leg` before resolving and burning debt, and withdrawal calls `load_leg` before resolving and burning supply. [9](#0-8) [10](#0-9) 

### Impact Explanation
This is a permanent freezing-of-funds condition for the affected `(hub_id, asset)` market. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot execute the pool legs needed by liquidation, and permissionless `update_indexes` cannot advance the market because each attempt repeats the overflowing accrual. [11](#0-10) 

The existing regression test demonstrates the terminal state: an 18-decimal market holding one billion whole tokens at 98% utilization eventually fails `update_indexes` with `MathOverflow`, while `withdraw` and `repay` subsequently fail with the same error even though the borrow index remains below `MAX_BORROW_INDEX_RAY`. [12](#0-11) 

### Likelihood Explanation
Likelihood is Medium rather than High because reaching the cliff requires an exceptionally large market and sustained high utilization over multiple accrual periods. [13](#0-12) 

No privileged action is needed to trigger the overflow once such a book exists: an unprivileged caller submits `Controller::update_indexes(caller, assets)` for the affected market, and any later user action forces the same accrual path. [14](#0-13) [15](#0-14)  A sufficiently funded attacker can also create the precondition through ordinary `supply` and `borrow`, while a market that has already grown close to the bound requires only the triggering accrual. [16](#0-15) 

### Recommendation
Enforce a state-dependent value bound in addition to the fixed index ceiling. Before minting debt and before each accrual step, reject or clamp growth so `borrowed × new_borrow_index` and `supplied × new_supply_index` remain representable; equivalently, derive an effective index cap from `i128::MAX / scaled_amount`. [17](#0-16) [6](#0-5) 

Entry caps should reserve headroom for plausible index growth rather than only validating the token amount at the current index. The accrual implementation should also avoid computing interest by subtracting two potentially overflowing total-debt values; calculate the bounded delta directly or use explicitly checked widened arithmetic with a defined saturation point. [2](#0-1) [7](#0-6) 

### Proof of Concept
The repository already contains a deterministic reproduction. It supplies `1_000_000_000 × 10^18` base units, borrows 98%, repeatedly advances one year, and observes `update_indexes`, `withdraw`, and `repay` fail with `MathOverflow` before the borrow index reaches its configured cap. [12](#0-11) 

The unprivileged sequence is:

```text
supply(
  caller = attacker,
  account_id = 0,
  spoke_id = S,
  assets = [ { hub_asset = BIG18, amount = 1_000_000_000 * 10^18 } ]
)

supply(
  caller = attacker,
  account_id = position_id,
  spoke_id = S,
  assets = [ { hub_asset = COLLATERAL, amount = sufficient_collateral } ]
)

borrow(
  caller = attacker,
  account_id = position_id,
  borrows = [ { hub_asset = BIG18, amount = 980_000_000 * 10^18 } ],
  to = attacker
)
```

After enough time for the borrow index to pass the market-specific value ceiling, call:

```text
update_indexes(
  caller = attacker,
  assets = [ HubAssetKey { hub_id = H, asset = BIG18 } ]
)
```

That call enters `markets::update_indexes`, forwards to the pool's `update_indexes`, and panics during accrual. [14](#0-13) [15](#0-14) [18](#0-17)  Subsequent `withdraw` or `repay` calls still synchronize before mutating and therefore repeat the same panic, leaving market funds permanently frozen absent a privileged code replacement. [8](#0-7) [19](#0-18)

### Citations

**File:** contracts/pool/src/interest.rs (L20-52)
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

/// Applies one compound step of `delta_ms` to indexes and protocol revenue.
///
/// The arithmetic lives in [`accrue_step`], shared with the read-only
/// `simulate_update_indexes` so the view and the mutator cannot drift.
fn accrue_chunk(env: &Env, cache: &mut Cache, delta_ms: u64) {
    let step = accrue_step(
        env,
        cache.params(),
        cache.borrowed(),
        cache.supplied(),
        cache.borrow_index(),
        cache.supply_index(),
        delta_ms,
    );

    cache.set_borrow_index(step.borrow_index);
    cache.set_supply_index(step.supply_index);
    cache.accrue_revenue(step.revenue_shares);
```

**File:** common/src/rates/index.rs (L11-45)
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

/// Grows `old_index` by distributing `rewards_increase` over the total value
/// currently supplied (`supplied * old_index`). The division rounds down.
///
/// Returns `old_index` unchanged if `supplied` or `rewards_increase` is zero,
/// or if the total supplied value is zero. Clamps the result between
/// `old_index` (itself capped at `MAX_SUPPLY_INDEX_RAY`) and
/// `MAX_SUPPLY_INDEX_RAY`, so the returned index never decreases and never
/// exceeds the cap.
pub fn update_supply_index(env: &Env, supplied: Ray, old_index: Ray, rewards_increase: Ray) -> Ray {
    if supplied == Ray::ZERO || rewards_increase == Ray::ZERO {
        return old_index;
    }

    let total_supplied_value = supplied.mul(env, old_index);

    if total_supplied_value == Ray::ZERO {
        return old_index;
    }

    let new_value = total_supplied_value.checked_add(env, rewards_increase);
    let grown = fp_core::mul_div_floor_saturating(env, new_value.raw(), RAY, supplied.raw());

    let bounded_old = old_index.raw().min(MAX_SUPPLY_INDEX_RAY);
    Ray::from(grown.min(MAX_SUPPLY_INDEX_RAY).max(bounded_old))
}
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

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** common/src/validation.rs (L48-69)
```rust
pub fn max_cap_for_decimals(asset_decimals: u32) -> i128 {
    let Some(exp) = RAY_DECIMALS.checked_sub(asset_decimals) else {
        return 0;
    };
    let upscale = 10i128
        .checked_pow(exp)
        .expect("10^(RAY_DECIMALS - asset_decimals) fits i128 for asset_decimals <= RAY_DECIMALS");
    i128::MAX / upscale
}

/// Panics with `CollateralError::AssetDecimalsTooHigh` if `asset_decimals`
/// exceeds `RAY_DECIMALS`, or with `CollateralError::InvalidBorrowParams` if
/// `cap` exceeds the value returned by `max_cap_for_decimals`.
pub fn require_cap_within_asset_domain(env: &Env, cap: i128, asset_decimals: u32) {
    if RAY_DECIMALS.checked_sub(asset_decimals).is_none() {
        panic_with_error!(env, CollateralError::AssetDecimalsTooHigh);
    }
    assert_with_error!(
        env,
        cap <= max_cap_for_decimals(asset_decimals),
        CollateralError::InvalidBorrowParams
    );
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

**File:** contracts/pool/src/ops/repay.rs (L36-59)
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
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    assert_with_error!(
        env,
        net_repay == 0 || burned.raw() > 0,
        GenericError::RepayRoundsToZeroShares
    );

    let position = position.checked_sub(env, burned);
    cache.burn_debt(burned);

    cache.credit_cash(net_repay);

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/ops/withdraw.rs (L53-81)
```rust
/// Runs withdraw accounting without transferring tokens.
///
/// Resolves full or partial close, burns shares, optionally withholds the
/// liquidation fee, and gates the final state before debiting cash.
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
    // Burn first: `protocol_fee_shares` caps the fee mint at `i128::MAX - supplied`.
    let remaining = burn_position(env, &mut cache, position, burned);
    let net_transfer = withhold_liquidation_fee(
        env,
        &mut cache,
        gross_amount,
        is_liquidation,
        entry.protocol_fee,
    );

    // A footprint-only close must not add a utilization gate to same-market
    // net settlement: it burns no shares and moves no cash.
    let empty_close = position.raw() == 0 && entry.action.amount == i128::MAX;
    gate_and_debit(env, &mut cache, net_transfer, is_liquidation || empty_close);

    let snapshot = cache.commit();
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

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }
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

**File:** contracts/pool/src/ops/market.rs (L60-72)
```rust
/// Accrues interest for each market in `hub_assets` and emits one state event
/// per market.
///
/// Always commits state so same-ledger simulation records the write footprint
/// needed if time advances before transaction inclusion.
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
    }
```
