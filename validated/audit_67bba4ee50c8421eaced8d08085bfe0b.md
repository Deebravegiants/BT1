### Title
RAY-scaled debt multiplication overflows before index cap, permanently freezing a market - (File: common/src/rates/index.rs)

### Summary
Interest accrual computes the new aggregate debt as `borrowed * new_borrow_index` before enforcing the intended borrow-index ceiling. A sufficiently large borrowed share balance can therefore make this RAY multiplication exceed `i128::MAX` while the index remains below `MAX_BORROW_INDEX_RAY`, causing every operation that accrues the market to revert with `MathOverflow`. [1](#0-0) [2](#0-1) 

### Finding Description
`global_sync` is executed before market mutations and repeatedly calls `accrue_step`, which eventually invokes `calculate_supplier_rewards`. [3](#0-2) [4](#0-3) 

Inside `calculate_supplier_rewards`, both `borrowed.mul(old_borrow_index)` and `borrowed.mul(new_borrow_index)` are evaluated unconditionally. [5](#0-4) 

The configured cap is applied only to the index returned by `update_borrow_index`; it does not bound the market-wide product `scaled_debt * index`. [6](#0-5) 

Consequently, the effective safety boundary is not `MAX_BORROW_INDEX_RAY`; it is approximately `index <= i128::MAX * RAY / borrowed`. Once a market exceeds that smaller boundary, accrual panics before the explicit index cap can protect it. [7](#0-6) [2](#0-1) 

The same overflow surface also exists for supply-side valuation through `supplied.mul(old_index)` in `update_supply_index` and `supply_index_reward_shortfall`. [8](#0-7) [9](#0-8) 

### Impact Explanation
This can permanently freeze all funds and operations for the affected `(hub_id, asset)` market. `update_indexes` calls `interest::global_sync` through `Cache::load` and the accrual path, while supply, borrow, withdraw, repay, liquidation, bad-debt processing, and strategy entrypoints likewise depend on market accrual/state resolution before completing. [10](#0-9) [11](#0-10) 

Once the stored scaled debt or scaled supply is large enough that the next index update crosses the `i128` valuation ceiling, subsequent transactions fail at the same multiplication rather than merely rejecting one oversized request. [12](#0-11) 

The repository’s own boundary test demonstrates the resulting denial of service: the market reaches `MathOverflow`, `withdraw` fails, and `repay` fails while the recorded borrow index is still below `MAX_BORROW_INDEX_RAY`. [13](#0-12) [14](#0-13) 

This is a market-wide freezing-of-funds impact rather than a fail-closed rejection of an invalid input: the attacker’s initial supply and borrow are protocol-valid amounts, and later accrual traps on aggregate valuation. [15](#0-14) [16](#0-15) 

### Likelihood Explanation
An unprivileged actor can reach the precondition by supplying a very large quantity of a listed high-decimals asset and borrowing enough of it to keep utilization high, using the permitted `supply`, `borrow`, and `update_indexes` flows. [10](#0-9) [17](#0-16) 

The likelihood is constrained by token supply, configured supply/borrow caps, collateral requirements, and market rate parameters; it is not reachable with ordinary balances. The repository test uses a one-billion-token, 18-decimals market, lifts caps to the listing maximum for that decimal width, and sustains 98% utilization. [18](#0-17) [19](#0-18) [20](#0-19) 

### Recommendation
Enforce a market-size-aware index bound before every `scaled * index` valuation. For scaled balance `S`, the safe raw index bound is approximately `floor(i128::MAX * RAY / S)`; compute that bound with widened or division-safe arithmetic and clamp `borrow_index`/`supply_index` to the minimum of the configured cap and this bound. [1](#0-0) [7](#0-6) 

Alternatively, compute aggregate old/new debt and supplied value in `I256`, saturate only the resulting valuation at a documented protocol ceiling, and commit the clamped index so later transactions remain executable. [21](#0-20) [4](#0-3) 

Also enforce corresponding scaled-position limits on `supply`, `borrow`, strategy debt minting, and bad-debt/index recovery paths so ordinary entries cannot leave a market one accrual step away from an unrecoverable multiplication overflow. [22](#0-21) [23](#0-22) 

### Proof of Concept
1. List or use a market with 18 decimals, a steep borrow curve, and caps at the protocol’s decimal-domain maximum.
2. From one attacker-controlled account, deposit `1_000_000_000 * 10^18` units of the target asset as market liquidity.
3. Deposit sufficient collateral and borrow `98%` of the target market through `borrow`.
4. Advance ledger time and call `update_indexes` for the market repeatedly.
5. Eventually `calculate_supplier_rewards` computes `borrowed * new_borrow_index` beyond `i128::MAX` while `new_borrow_index < MAX_BORROW_INDEX_RAY`.
6. The accrual reverts with `MathOverflow`; subsequent `withdraw`, `repay`, liquidation, and further index updates repeat the same accrual and remain blocked.

The concrete regression is already encoded in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`, which asserts `MATH_OVERFLOW`, confirms `borrow_index < MAX_BORROW_INDEX_RAY`, and verifies both withdrawal and repayment remain failing. [24](#0-23) [25](#0-24)

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

**File:** common/src/rates/index.rs (L29-44)
```rust
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
```

**File:** common/src/rates/index.rs (L53-63)
```rust
pub fn supply_index_reward_shortfall(
    env: &Env,
    supplied: Ray,
    old_index: Ray,
    new_index: Ray,
    rewards_increase: Ray,
) -> Ray {
    let distributed = supplied
        .mul(env, new_index)
        .checked_sub(env, supplied.mul(env, old_index));
    rewards_increase.checked_sub(env, distributed)
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

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
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

**File:** contracts/pool/src/interest.rs (L39-52)
```rust
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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** contracts/pool/src/cache/scale.rs (L15-27)
```rust
impl Cache {
    /// Utilization = total borrowed value / total supplied value (RAY).
    ///
    /// Returns zero when there is no supply.
    pub(crate) fn calculate_utilization(&self) -> Ray {
        if self.supplied == Ray::ZERO {
            return Ray::ZERO;
        }
        let total_borrowed = scaled_to_original(&self.env, self.borrowed, self.borrow_index);
        let total_supplied = scaled_to_original(&self.env, self.supplied, self.supply_index);

        utilization(&self.env, total_borrowed, total_supplied)
    }
```

**File:** contracts/pool/src/cache/scale.rs (L29-47)
```rust
    /// Converts an asset deposit into scaled supply shares (floor at the supply index).
    pub(crate) fn calculate_scaled_supply(&self, amount: i128) -> Ray {
        calculate_scaled_supply(
            &self.env,
            amount,
            self.params.asset_decimals,
            self.supply_index,
        )
    }

    /// Converts an asset borrow into scaled debt shares (ceil at the borrow index).
    pub(crate) fn calculate_scaled_borrow(&self, amount: i128) -> Ray {
        calculate_scaled_borrow(
            &self.env,
            amount,
            self.params.asset_decimals,
            self.borrow_index,
        )
    }
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L23-38)
```rust
const YEAR_SECS: u64 = 31_556_926;
const BILLION: i128 = 1_000_000_000;

/// Steep XLM stress curve: 175 percent max borrow rate, optimal at 75 percent.
fn xlm_curve() -> MarketParamsPreset {
    MarketParamsPreset {
        max_borrow_rate: RAY * 175 / 100,
        base_borrow_rate: RAY / 100,
        slope1: RAY * 4 / 100,
        slope2: RAY * 10 / 100,
        slope3: RAY * 150 / 100,
        mid_utilization: RAY * 50 / 100,
        optimal_utilization: RAY * 75 / 100,
        max_utilization: RAY,
        reserve_factor: 2000,
    }
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-320)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
#[test]
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-333)
```rust
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L335-356)
```rust
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

**File:** contracts/pool/README.md (L101-114)
```markdown
| `__constructor` | `fn __constructor(env: Env, admin: Address)` | deployer, once | Sets `admin` as the Ownable owner. |
| `create_market` | `fn create_market(env: Env, hub_id: u32, params: MarketParamsRaw)` | owner | Creates the market for `(hub_id, params.asset_id)` with both indexes at `RAY`. |
| `update_params` | `fn update_params(env: Env, hub_asset: HubAssetKey, model: InterestRateModel)` | owner | Accrues on the old curve, then writes the new rate model. |
| `update_indexes` | `fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>)` | owner | Accrues each market to now, and writes only if time elapsed. |
| `supply` | `fn supply(env: Env, entries: Vec<PoolSupplyEntry>) -> Vec<PoolPositionMutation>` | owner | Mints supply shares and credits cash, one mutation returned per entry. |
| `borrow` | `fn borrow(env: Env, receiver: Address, entries: Vec<PoolBorrowEntry>) -> Vec<PoolPositionMutation>` | owner | Mints debt shares, debits cash, and transfers the asset to `receiver`. |
| `withdraw` | `fn withdraw(env: Env, receiver: Address, is_liquidation: bool, entries: Vec<PoolWithdrawEntry>) -> Vec<PoolPositionMutation>` | owner | Burns supply shares and transfers the net amount to `receiver`. |
| `repay` | `fn repay(env: Env, payer: Address, actions: Vec<PoolAction>) -> Vec<PoolPositionMutation>` | owner | Burns debt shares, credits the net repay, and refunds overpayment to `payer`. |
| `net_settle` | `fn net_settle(env: Env, entry: PoolNetSettleEntry) -> PoolNetSettleResult` | owner | Offsets one user's supply against their own debt. Takes one entry, not a batch. |
| `seize_positions` | `fn seize_positions(env: Env, entries: Vec<PoolSeizeEntry>)` | owner | Writes off bad debt on the borrow side, or books a seized deposit as revenue. Returns nothing. |
| `flash_loan` | `fn flash_loan(env: Env, hub_asset: HubAssetKey, initiator: Address, receiver: Address, amount: i128, data: Bytes) -> i128` | owner | Pays out, calls `execute_flash_loan` on `receiver`, pulls principal plus fee back. Returns the fee. |
| `create_strategy` | `fn create_strategy(env: Env, receiver: Address, action: PoolAction, charge_fee: bool) -> PoolStrategyMutation` | owner | Mints debt, books the optional fee as revenue, and sends `amount - fee` to `receiver`. |
| `recapitalize` | `fn recapitalize(env: Env, hub_asset: HubAssetKey, payer: Address, amount: i128) -> PoolAmountMutation` | owner | Credits cash up to the backing shortfall and refunds the excess to `payer`. |
| `claim_revenue` | `fn claim_revenue(env: Env, hub_asset: HubAssetKey) -> PoolAmountMutation` | owner | Burns revenue shares and transfers the proceeds to the owner. |
```

**File:** common/src/math/fp_core.rs (L148-159)
```rust
pub fn mul_div_floor(env: &Env, x: i128, y: i128, d: i128) -> i128 {
    require_nonzero_divisor(env, d);
    if let Some(quotient) = x
        .checked_mul(y)
        .and_then(|product| div_floor_i128(product, d))
    {
        return quotient;
    }
    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    let nonneg = quotient_is_nonnegative(x, y, d);
    to_i128(env, &div_floor_i256(env, &x256.mul(&y256), &d256, nonneg))
}
```
