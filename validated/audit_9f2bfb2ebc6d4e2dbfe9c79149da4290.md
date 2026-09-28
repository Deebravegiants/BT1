### Title
Interest accrual can permanently freeze a market through RAY-value `i128` overflow - (`common/src/rates/simulate.rs`)

### Summary
`accrue_step` multiplies the stored scaled borrow total by the borrow index before applying the borrow-index cap, so sufficiently large market totals can exceed `i128` even though the index itself remains below `MAX_BORROW_INDEX_RAY`. [1](#0-0)  An unprivileged caller can create and leverage a sufficiently large market through `supply` and `borrow`, and any caller can later trigger the overflowing accrual through `update_indexes`. [2](#0-1) [3](#0-2) 

### Finding Description
Market balances are stored as RAY-scaled share amounts, and `scaled_to_original` computes `scaled * index / RAY` through a checked fixed-point multiplication. [4](#0-3)  `accrue_step` calls `scaled_to_original` for both `borrowed` and `supplied` before it calculates utilization or updates the indexes. [5](#0-4)  Although `update_borrow_index` caps the resulting index at `MAX_BORROW_INDEX_RAY`, that cap is applied after the unscaled balance multiplication and therefore does not prevent a balance-value overflow. [6](#0-5) 

Once the stored scaled balance and current index make `borrowed * borrow_index` or `supplied * supply_index` unrepresentable in `i128`, the accrual raises `MathOverflow` and aborts the transaction. [7](#0-6)  Because pool mutations call `global_sync` before executing the requested operation, later supply, borrow, withdrawal, repayment, liquidation settlement, and revenue operations against that market hit the same failing computation. [8](#0-7) 

The repository already contains a regression-style demonstration: a 1-billion whole-token market with 18 decimals and 98% utilization eventually fails inside `scaled_to_original` before the index cap is reached, after which even a 1-unit withdrawal or 1-token repayment returns `MATH_OVERFLOW`. [9](#0-8)  The protocol documentation explicitly acknowledges that market totals can stop fitting the RAY domain before the index ceiling and that this can block repayment and withdrawal because those operations accrue first. [10](#0-9) 

### Impact Explanation
The affected market becomes permanently unable to accrue, so user collateral cannot be withdrawn and borrower debt cannot be repaid through the normal controller paths. [11](#0-10)  Liquidation and bad-debt processing also need pool accrual or pool settlement and cannot bypass the overflowing market-state update, leaving otherwise recoverable value and protocol revenue stuck. [8](#0-7) 

### Likelihood Explanation
The attack requires a very large supplied or borrowed balance and enough elapsed time for index growth to make the unscaled RAY value exceed `i128`, rather than merely submitting one malformed price or one overflowing integer. [12](#0-11)  A single unprivileged account owner can nevertheless set up the required state with `supply(caller, 0, spoke_id, assets)`, followed by `borrow(caller, account_id, borrows, to)`, while `update_indexes(caller, assets)` is permissionless for triggering and confirming the failure. [13](#0-12)  The substantial capital and accrual requirements reduce the likelihood, but the resulting permanent market-wide freeze makes this a valid Medium-severity analog rather than a benign transaction revert. [9](#0-8) 

### Recommendation
Bound market scaled totals so every value later passed to `scaled_to_original` cannot overflow at the maximum reachable index, or make index growth stop before the balance-index product leaves `i128`. [4](#0-3)  Accrual should compute unscaled values with an overflow-aware path and clamp or otherwise safely cap debt growth when the representable-value boundary is reached, while still allowing repayments and withdrawals to proceed. [14](#0-13)  Regression tests should cover the boundary at which `scaled_to_original` would fail and verify that `withdraw`, `repay`, liquidation settlement, and `update_indexes` remain callable. [15](#0-14) 

### Proof of Concept
1. Create a large 18-decimal market and supply `1_000_000_000 * 10^18` base units to it. [16](#0-15) 
2. Supply enough separate collateral and borrow approximately 98% of the large market's liquidity. [17](#0-16) 
3. Repeatedly call `controller.update_indexes(caller, vec![large_market_key])` as ledger time advances; once `borrowed * borrow_index / RAY` exceeds `i128`, the call fails with `MathOverflow`. [18](#0-17) [5](#0-4) 
4. Subsequent `withdraw(caller, supplier_account, vec![(large_market_key, 1)], None)` and `repay(caller, borrower_account, vec![(large_market_key, 10^18)])` calls fail because each pool mutation first runs the same overflowing accrual. [8](#0-7) [19](#0-18)

### Citations

**File:** common/src/rates/simulate.rs (L51-87)
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
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);

    let new_supply_index = update_supply_index(env, supplied, supply_index, supplier_rewards);
    let supplier_shortfall = supply_index_reward_shortfall(
        env,
        supplied,
        supply_index,
        new_supply_index,
        supplier_rewards,
    );

    let protocol_reward = protocol_fee.checked_add(env, supplier_shortfall);
    // Shares are valued at the new supply index, which the caller stores for
    // this step.
    let revenue_shares = if protocol_reward == Ray::ZERO {
        Ray::ZERO
    } else {
        protocol_fee_shares(env, protocol_reward, new_supply_index, supplied)
    };
```

**File:** contracts/controller/src/lib.rs (L93-114)
```rust
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

**File:** common/src/math/fp_core.rs (L104-118)
```rust
/// Computes `x * y / d` rounded half up. Requires `x >= 0`, `y >= 0`, and `d > 0`; a
/// `debug_assert` checks this in debug builds. Panics with `GenericError::DivisionByZero` if
/// `d == 0`, and with `GenericError::MathOverflow` if any other precondition is violated or if
/// the result does not fit in `i128`.
pub fn mul_div_half_up(env: &Env, x: i128, y: i128, d: i128) -> i128 {
    // The zero check runs first so debug and release builds agree on a zero
    // divisor: both surface `DivisionByZero` rather than tripping the assert.
    require_nonzero_divisor(env, d);
    debug_assert!(
        x >= 0 && y >= 0 && d > 0,
        "mul_div_half_up: non-negative x, y and positive d"
    );
    try_mul_div_half_up(env, x, y, d)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
}
```

**File:** contracts/pool/src/interest.rs (L16-33)
```rust
/// Accrues borrow/supply indexes from `last_timestamp` to the cache's current time.
///
/// No-op when no time has elapsed. Splits long gaps into max-sized compound
/// windows, then sets `last_timestamp` to `current_timestamp`.
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

**File:** docs/reference/formulas.md (L425-430)
```markdown
| Asset decimals 0..=18 | Exact token-to-RAY upscaling. Below 3: collateral only, no flash loans, no liquidation fee, its account's only supply position, at least 2 whole units while in debt |
| Both indexes initially RAY; ceiling 10^36 | 10^9 times initial index; protocol constants |
| Supply-index floor 10^24 | At most 1,000 times the shares minted at index one for the same deposit |
| Borrow APR maximum 2 RAY | 200% annual rate; not a bound on balance growth alone |
| Token-to-RAY input maximum `i128::MAX / 10^(27-d)` | About 170.14 billion whole tokens, before other limits |
| Deposit conversion at the supply-index floor | About 170.14 million whole tokens before scaled-share overflow |
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

**File:** docs/reference/endpoints.md (L24-38)
```markdown
| `supply(caller: Address, account_id: u64, spoke_id: u32, assets: Vec<(HubAssetKey, i128)>) -> u64` | Existing assets only for third parties | gated | Supply measured deposits; id 0 creates Normal account. |
| `borrow(caller: Address, account_id: u64, borrows: Vec<(HubAssetKey, i128)>, to: Option<Address>)` | NFT owner/delegate | gated | Debt booked to account; recipient defaults to caller. |
| `withdraw(caller: Address, account_id: u64, withdrawals: Vec<(HubAssetKey, i128)>, to: Option<Address>) -> Vec<(HubAssetKey, i128)>` | NFT owner/delegate | open | Zero means full withdrawal; returns the amounts paid. |
| `repay(caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>)` | None | open | Anyone can repay; excess returns to caller. |
| `liquidate(liquidator: Address, account_id: u64, debt_payments: Vec<(HubAssetKey, i128)>, seize_mode: SeizeMode) -> u64` | None; credit receiver owner/delegate | open | Pro-rata seizure; Transfer returns 0, Credit returns receiver id. |
| `clean_bad_debt(caller: Address, account_id: u64)` | None | open | Debt exceeds collateral and collateral <= $5; socialize and burn NFT. |
| `flash_loan(caller: Address, asset: HubAssetKey, amount: i128, receiver: Address, data: Bytes)` | None | gated | Wasm callback; pool pulls exact principal plus fee. |
| `flash_position(caller: Address, account_id: u64, spoke_id: u32, mode: PositionMode, debt: HubAssetKey, amount: i128, receiver: Address, data: Bytes, collaterals: Vec<(HubAssetKey, i128)>, refund_assets: Vec<Address>) -> u64` | NFT owner/delegate for existing id | gated | Mint fee-free debt; deposit declared collateral that the callback delivers. |
| `multiply(caller: Address, account_id: u64, spoke_id: u32, collateral: HubAssetKey, debt_to_flash_loan: i128, debt: HubAssetKey, mode: PositionMode, swap: Bytes, initial_payment: Option<(HubAssetKey, i128)>, convert_swap: Option<Bytes>) -> u64` | NFT owner/delegate for existing id | gated | Borrow, swap and supply; optional initial capital. |
| `swap_debt(caller: Address, account_id: u64, existing_debt: HubAssetKey, amount: i128, new_debt: HubAssetKey, swap: Bytes)` | NFT owner/delegate | gated | Borrow new debt, then repay existing debt with the swap output. The new borrow must fit its borrow cap and the borrow-position limit before repayment. |
| `swap_collateral(caller: Address, account_id: u64, current: HubAssetKey, amount: i128, new: HubAssetKey, swap: Bytes)` | NFT owner/delegate | gated | Withdraw, convert and redeposit collateral. |
| `repay_debt_with_collateral(caller: Address, account_id: u64, collateral: HubAssetKey, collateral_amount: i128, debt: HubAssetKey, swap: Bytes, close_position: bool)` | NFT owner/delegate | gated | Direct same-market netting or swap; optional full close. |
| `migrate_from_blend(caller: Address, account_id: u64, spoke_id: u32, hub_id: u32, blend_pool: Address, collateral_assets: Vec<Address>, supply_assets: Vec<Address>, debt_caps: Vec<(Address, i128)>) -> u64` | NFT owner/delegate for existing id | gated | Migrate caller’s position from approved Blend pool. |
| `update_indexes(caller: Address, assets: Vec<HubAssetKey>)` | None | gated | Accrue specified markets. |
| `claim_revenue(caller: Address, assets: Vec<HubAssetKey>) -> Vec<i128>` | None | gated | Pay only configured accumulator; return controller receipts. |
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
