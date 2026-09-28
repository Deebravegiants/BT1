### Title
RAY-domain value overflow permanently freezes a saturated lending market - (File: common/src/rates/scaling.rs)

### Summary
A large market can grow until `scaled_amount * index` no longer fits in `i128`, even though both indexes remain below their configured `10^36` cap. Because every pool mutation synchronizes interest before executing the requested operation, the resulting `MathOverflow` prevents repayment, withdrawal, liquidation, recapitalization, and index updates for that market, permanently trapping its pool funds absent a code upgrade.

### Finding Description
`accrue_step` first converts market-wide scaled debt and supply into RAY-denominated values through `scaled_to_original`. [1](#0-0)  `scaled_to_original` delegates to `Ray::mul`, which uses `mul_div_half_up` and panics when the representable result exceeds `i128::MAX`. [2](#0-1) [3](#0-2) 

The borrow index is clamped only after multiplying the old index by the interest factor; it does not bound the market’s `borrowed * borrow_index` or `supplied * supply_index` values. [4](#0-3)  Consequently, a sufficiently large scaled balance can overflow while the index itself remains valid.

`ops::load_leg` calls `synced_market`, and `synced_market` always runs `interest::global_sync` before the mutation logic. [5](#0-4)  Repayment and withdrawal both reach `load_leg` before resolving or burning shares. [6](#0-5) [7](#0-6)  The public controller exposes the corresponding `repay`, `withdraw`, `liquidate`, `clean_bad_debt`, and `update_indexes` routes. [8](#0-7) [9](#0-8) 

### Impact Explanation
This is permanent freezing of user funds and protocol insolvency risk, not merely a bounded per-call denial of service. Once `borrowed * borrow_index` or `supplied * supply_index` crosses the `i128` boundary, each subsequent mutation panics during mandatory accrual before it can reduce the oversized scaled balance.

Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot unwind the account, and cleanup or recapitalization cannot reach the state-changing logic because those calls also synchronize first. Pool cash remains held by the contract while all recovery paths fail with `MathOverflow`.

### Likelihood Explanation
The condition is reachable only in an extremely large, interest-bearing market. A market must admit balances close to the protocol’s maximum token-to-RAY domain and sustain enough utilization and time for an index multiplier to push a scaled value beyond `i128::MAX`.

The regression test demonstrates the exact reachable sequence: a one-billion-whole-token, 18-decimal market at 98% utilization eventually causes `update_indexes` to return `MATH_OVERFLOW` below `MAX_BORROW_INDEX_RAY`, after which even a one-unit withdrawal and a small repayment fail. [10](#0-9)  A single unprivileged borrower can create the high-utilization leg on any listed market whose configured caps and available liquidity permit the required size, while third-party suppliers provide the trapped funds.

### Recommendation
Track and enforce separate representable-value ceilings for `borrowed * borrow_index` and `supplied * supply_index`, rather than relying on index caps and admission-time token caps. Before increasing an index, compute the post-accrual values with checked arithmetic and clamp accrual or reject growth early enough that exits remain possible.

An emergency exit path could also skip index accrual for conservative operations such as full repayment, full withdrawal, bad-debt cleanup, or recapitalization. Such a path must preserve existing indexes and rounding so it cannot mint unbacked value while bypassing the overflowing multiplication.

### Proof of Concept
The repository already contains a deterministic reproduction in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`. It creates an 18-decimal market, supplies `1_000_000_000 * 10^18` units, borrows 98% of the principal, advances time until `update_indexes` fails, verifies that the index cap has not engaged, and then verifies that withdrawal and repayment both return `MATH_OVERFLOW`. [10](#0-9) 

The unprivileged transaction sequence is:

1. Victims call `supply(caller, account_id, spoke_id, [(hub_asset, amount)])` to build pool liquidity.
2. The attacker supplies sufficient collateral through `supply` and draws high utilization through `borrow(caller, account_id, [(hub_asset, debt)], to)`.
3. Time elapses while borrow interest compounds.
4. Any caller invokes `update_indexes`, `repay`, `withdraw`, `liquidate`, `clean_bad_debt`, or `recapitalize` for the market.
5. `global_sync` executes `accrue_step`, `scaled_to_original` computes a value larger than `i128::MAX`, and the call reverts before the requested recovery action can run.

### Citations

**File:** common/src/rates/simulate.rs (L60-64)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

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

**File:** contracts/pool/src/ops/withdraw.rs (L53-68)
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
```

**File:** contracts/controller/src/lib.rs (L120-164)
```rust
    fn withdraw(
        env: Env,
        caller: Address,
        account_id: u64,
        withdrawals: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) -> Vec<(HubAssetKey, i128)> {
        positions::process_withdraw(&env, &caller, account_id, &withdrawals, to)
    }

    /// Repays `account_id`'s debt using measured payments from the caller.
    /// Anyone may repay; excess payments are refunded to the caller.
    fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>) {
        positions::process_repay(&env, &caller, account_id, &payments);
    }

    /// Repays debt and seizes collateral at a health-factor-based bonus.
    /// Permissionless, including self-liquidation; requires liquidator authorization.
    /// Residual bad debt is socialized only at or below the collateral dust cap.
    ///
    /// `Transfer` pays pool cash and returns `0`. `Credit(id)` moves net supply
    /// shares to a different, authorized Normal-mode account on the same spoke;
    /// `Credit(0)` creates one. Credit mode needs no free collateral liquidity
    /// and returns the receiving account id.
    fn liquidate(
        env: Env,
        liquidator: Address,
        account_id: u64,
        debt_payments: Vec<(HubAssetKey, i128)>,
        seize_mode: SeizeMode,
    ) -> u64 {
        positions::liquidation::process_liquidation(
            &env,
            &liquidator,
            account_id,
            &debt_payments,
            seize_mode,
        )
    }

    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
```

**File:** contracts/pool/src/lib.rs (L174-180)
```rust
    /// Accrues interest for each market in `hub_assets` through the current
    /// ledger time. Commits state even with no elapsed time to reserve the write
    /// footprint, and emits its market state event. Restricted to the owner.
    #[only_owner]
    fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>) {
        ops::market::accrue(&env, hub_assets);
    }
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-356)
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
