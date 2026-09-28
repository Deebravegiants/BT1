### Title
Unbounded scaled market values permanently freeze a large market through `i128` overflow - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary
`accrue_step` converts aggregate scaled supply and debt into RAY values with `scaled.mul(index)` before calculating utilization. When a market’s admitted scaled balance is large enough, index growth eventually makes that product exceed `i128::MAX`, so every subsequent operation that synchronizes the market reverts on `MathOverflow`. This leaves suppliers unable to withdraw and borrowers or third parties unable to repay or unwind the position. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
A caller can create this state through `Controller::supply` and `Controller::borrow`: one account supplies a large supported asset balance, while another account supplies collateral and borrows most of that market. [4](#0-3) [5](#0-4)  Each pool mutation calls `synced_market`, which loads the market and runs `interest::global_sync` before applying the operation. [3](#0-2)  `global_sync` repeatedly calls `accrue_step` for elapsed time, and `accrue_step` unconditionally evaluates both aggregate scaled balances at the current indexes. [6](#0-5) [1](#0-0) 

The borrow index is capped only after the new index is calculated, and the cap does not bound the later `scaled_amount * index` product against `i128::MAX`. [7](#0-6)  An 18-decimal market can admit approximately 170 billion whole-token scaled input before token-to-RAY conversion overflows, while one billion whole tokens produces a scaled balance of `1e36` and crosses the value ceiling once its index reaches roughly `170 * RAY`. [8](#0-7) [9](#0-8) 

The repository’s focused test demonstrates this cliff: after a one-billion-token, 98%-utilized market accrues until `update_indexes` fails with `MathOverflow`, both `withdraw` and `repay` fail with the same error because they attempt accrual first. [10](#0-9) 

### Impact Explanation
This is permanent freezing of user funds rather than ordinary fail-closed validation: once the aggregate product overflows, ledger time cannot move backward, the stored index does not decrease through normal accrual, and every repayment, withdrawal, liquidation leg, index update, or recapitalization that synchronizes the market reverts before effects are committed. [11](#0-10) [12](#0-11) 

Suppliers lose access to their underlying deposits, borrowers cannot reduce unsafe debt, and liquidators cannot progress through pool operations that require the same synchronized market cache. [13](#0-12) [14](#0-13) [15](#0-14) 

### Likelihood Explanation
The trigger does not require privileged access, leaked keys, malformed protocol input, or a third-party failure: it only requires a market to reach the protocol’s own numeric domain through permitted supply, borrow, and passive accrual. [16](#0-15) [17](#0-16)  The required amount is economically large, but it remains below the documented admitted maximum for an 18-decimal asset and can be supplied by an ordinary market participant when token supply permits it. [8](#0-7) [18](#0-17) 

High utilization causes the borrow index to compound faster than the supply index, while the aggregate multiplication remains unconditional even after the borrow-index cap stops further index growth. [19](#0-18) [20](#0-19) 

### Recommendation
Prevent aggregate `scaled_amount * index` from being evaluated as an unbounded `i128` value. Compare the scaled amount and index before multiplication, or use a wider exact intermediate representation for market-level utilization and accrual calculations. Additionally, enforce a market-level scaled-size/index-product bound during supply and accrual before the RAY value can exceed `i128::MAX`, leaving enough margin for liquidation, repayment, withdrawal, and bad-debt settlement paths. The regression test at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs` should be changed from pinning the freeze to asserting that large markets continue to repay and withdraw after reaching the configured index boundary. [2](#0-1) [10](#0-9) 

### Proof of Concept
```rust
let principal: i128 = 1_000_000_000 * 10i128.pow(18); // 1e9 whole tokens.
let debt: i128 = principal * 98 / 100;

// BOB supplies liquidity to the 18-decimal market.
controller.supply(
    bob,
    0,                 // create BOB's account
    spoke_id,
    vec![&env, (big18_hub_asset, principal)],
);

// ALICE supplies sufficient collateral in another market.
let alice_id = controller.supply(
    alice,
    0,
    spoke_id,
    vec![&env, (collateral_hub_asset, collateral_amount)],
);

// Borrow almost all BIG18 liquidity.
controller.borrow(
    alice,
    alice_id,
    vec![&env, (big18_hub_asset, debt)],
    None,
);

// Advance ledger time and call permissionless index updates until
// scaled_supply * supply_index or scaled_debt * borrow_index exceeds i128::MAX.
loop {
    advance_ledger();
    if controller.try_update_indexes(vec![&env, big18_hub_asset]).is_err() {
        break;
    }
}

// Every path that synchronizes the market now reverts with MathOverflow.
controller.withdraw(bob, bob_id, vec![&env, (big18_hub_asset, 1)], None);
controller.repay(alice, alice_id, vec![&env, (big18_hub_asset, 1)]);
```

The existing harness test creates the same shape with `principal = BILLION * 10^18`, borrows `98%`, advances time until `try_update_indexes` returns `MathOverflow`, and then confirms that withdrawal and repayment also return `MathOverflow`. [21](#0-20)

### Citations

**File:** common/src/rates/simulate.rs (L60-69)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** contracts/pool/src/ops/mod.rs (L30-33)
```rust
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
```

**File:** contracts/pool/src/ops/mod.rs (L42-47)
```rust
/// Validates `action.amount ≥ 0`, syncs the market, and returns (cache, scaled position).
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
}
```

**File:** contracts/controller/src/lib.rs (L94-114)
```rust
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

**File:** contracts/pool/src/interest.rs (L20-30)
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

**File:** docs/reference/formulas.md (L425-430)
```markdown
| Asset decimals 0..=18 | Exact token-to-RAY upscaling. Below 3: collateral only, no flash loans, no liquidation fee, its account's only supply position, at least 2 whole units while in debt |
| Both indexes initially RAY; ceiling 10^36 | 10^9 times initial index; protocol constants |
| Supply-index floor 10^24 | At most 1,000 times the shares minted at index one for the same deposit |
| Borrow APR maximum 2 RAY | 200% annual rate; not a bound on balance growth alone |
| Token-to-RAY input maximum `i128::MAX / 10^(27-d)` | About 170.14 billion whole tokens, before other limits |
| Deposit conversion at the supply-index floor | About 170.14 million whole tokens before scaled-share overflow |
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

**File:** contracts/pool/src/ops/repay.rs (L40-45)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
```

**File:** contracts/pool/src/ops/withdraw.rs (L61-68)
```rust
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
    // Burn first: `protocol_fee_shares` caps the fee mint at `i128::MAX - supplied`.
    let remaining = burn_position(env, &mut cache, position, burned);
    let net_transfer = withhold_liquidation_fee(
```
