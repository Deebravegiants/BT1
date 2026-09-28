### Title
Permissionless index accrual can permanently freeze a saturated market before its index cap - (File: common/src/rates/simulate.rs) [1](#0-0) 

### Summary
A market can reach a state where `borrowed_scaled * borrow_index` exceeds `i128::MAX` before `borrow_index` reaches `MAX_BORROW_INDEX_RAY`; the next accrual then panics in `accrue_step` while converting scaled balances to underlying values. [2](#0-1) [3](#0-2) 

Because every pool mutation loads the market through `synced_market`, which calls `global_sync` before executing the operation, the same arithmetic panic blocks repayments, withdrawals, liquidations, recapitalization, parameter updates, and keeper index updates. [4](#0-3) [5](#0-4) 

### Finding Description
`accrue_step` first calls `scaled_to_original` for total borrowed and total supplied balances to compute utilization. [6](#0-5)  The same overflowable `scaled * index` multiplication is then used to calculate the old and new total debt before deriving interest. [7](#0-6) 

`update_borrow_index` caps the index only after multiplying the old index by the interest factor; it does not cap the index based on the market's scaled borrow balance. [3](#0-2)  The protocol documentation acknowledges that accrued totals can overflow before the index ceiling and that repayment and withdrawal can be blocked because they accrue first. [8](#0-7) 

A permissionless caller can trigger the terminal failure through `update_indexes(caller, assets)`, where `assets` is a `Vec<HubAssetKey>` containing the saturated market. [9](#0-8) [10](#0-9)  The pool's normal flow loads the market, runs `global_sync`, and only then applies the requested operation, so there is no ordinary exit path that skips the failing accrual. [11](#0-10) [12](#0-11) 

### Impact Explanation
Once scaled borrow value exceeds the representable `i128` range, all interest-bearing activity on the market reverts with `MathOverflow`. [13](#0-12)  Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot execute the underlying pool legs, and `update_indexes` cannot persist a later timestamp because `accrue_chunk` panics before `mark_accrued` runs. [14](#0-13) [5](#0-4) 

This is a permanent market freeze rather than a bounded fail-closed rejection: every subsequent timestamp still requires the same overflowing conversion before any state-changing logic can run, and even an owner-driven parameter update routes through an accrual-first pool call. [4](#0-3) [15](#0-14)  The repository's own regression test demonstrates that once the cliff is reached, both withdrawal and repayment return `MathOverflow`. [16](#0-15) 

### Likelihood Explanation
The state requires an exceptionally large market, sustained high utilization, and enough elapsed time for the index multiplier to exceed roughly `i128::MAX / borrowed_scaled`; the tested fixture uses one billion 18-decimal tokens at 98% utilization on a steep 175%-maximum rate curve. [17](#0-16)  Those parameters and balances are within the protocol's admitted numeric domain rather than malformed inputs: token scaling admits approximately 170 billion whole tokens before its own cap, while capped indexes do not guarantee that accrued position values remain representable. [18](#0-17) 

The triggering call is fully permissionless because `update_indexes` is intended keeper maintenance and only chooses accrual timing. [19](#0-18)  Exploitation therefore does not require leaked keys, oracle manipulation, reentrancy, or a malformed token; it requires a market scale and rate profile that governance is permitted to configure. [20](#0-19) 

### Recommendation
Do not allow accrual to depend on an `i128` product that can exceed the representable total-value domain. [2](#0-1)  Constrain `new_borrow_index` to a market-specific safe ceiling such as `min(MAX_BORROW_INDEX_RAY, floor((i128::MAX - 1) / borrowed_scaled))` before calculating rewards, and apply the analogous bound to `supply_index` against `supplied_scaled`. [3](#0-2) [21](#0-20) 

Alternatively, perform utilization and accrued-total calculations in `I256` and deliberately saturate those values before deriving the index, ensuring the mutating path can always commit `last_timestamp` and leave the market operable. [1](#0-0)  Add a regression test proving that `update_indexes`, `repay`, `withdraw`, liquidation pool legs, `recapitalize`, and owner parameter updates remain callable at the safe-index boundary. [22](#0-21) [16](#0-15) 

### Proof of Concept
The repository already contains a deterministic proof in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`. [23](#0-22) 

1. Create an 18-decimal market using the supported steep XLM rate curve and another collateral market. [20](#0-19) 
2. Supply `1_000_000_000 * 10^18` units and borrow `980_000_000 * 10^18` units. [24](#0-23) 
3. Advance ledger time in yearly intervals and call the permissionless `update_indexes` path for the market. [25](#0-24) 
4. When the index crosses the scaled-value ceiling, `update_indexes` returns `MathOverflow` while `borrow_index` remains below `MAX_BORROW_INDEX_RAY`. [26](#0-25) 
5. Subsequent `withdraw` and `repay` calls revert with the same `MathOverflow` because both enter the pool through `synced_market` and execute `global_sync` first. [27](#0-26) [4](#0-3)

### Citations

**File:** common/src/rates/simulate.rs (L51-72)
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

**File:** common/src/rates/index.rs (L80-83)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);
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

**File:** docs/reference/endpoints.md (L37-40)
```markdown
| `update_indexes(caller: Address, assets: Vec<HubAssetKey>)` | None | gated | Accrue specified markets. |
| `claim_revenue(caller: Address, assets: Vec<HubAssetKey>) -> Vec<i128>` | None | gated | Pay only configured accumulator; return controller receipts. |
| `update_account_threshold(caller: Address, has_risks: bool, account_ids: Vec<u64>)` | None | gated | Refresh LTV; optional risk refresh requires final HF >= 1.05. |
| `recapitalize(payer: Address, hub_asset: HubAssetKey, amount: i128) -> i128` | None | open | Measured backing injection; refund surplus; return amount applied. |
```

**File:** scripts/permissionless_entrypoints.txt (L69-77)
```text
controller::supply | caller-auth | INV-AUTH-03, INV-ACCT-03 | Anyone may top up an account they do not own, but only for hub assets it already holds a supply position in; a caller that is neither the owner nor an active delegate cannot open a new asset slot, and account_id 0 creates an account owned by the caller.
controller::repay | caller-auth | INV-AUTH-03, INV-ACCT-03 | Anyone may repay any account's debt. Funds are pulled from the caller's own balance and credited from the measured receipt; the target's liabilities can only fall.
controller::liquidate | caller-auth | INV-AUTH-03, INV-LIQ-01, INV-LIQ-02 | Anyone may liquidate an account whose health factor is below one, including the account's own owner; in Credit seize mode the receiving account must be a different account that the liquidator owns or is an active delegate of, and seizure stays coupled to the debt actually repaid.
controller::clean_bad_debt | caller-auth | INV-AUTH-03, INV-LIQ-04 | Anyone may socialize an insolvent account's residual debt, but only once its remaining collateral is at or below the dust threshold; only the owner-gated force_socialize_bad_debt omits the dust cap.
controller::recapitalize | caller-auth | INV-AUTH-03, INV-ACCT-02, INV-ACCT-03 | Anyone may donate their own funds to cover a market's backing shortfall; only the measured receipt up to the shortfall is applied and the excess is refunded to the payer.
controller::update_indexes | caller-auth | INV-AUTH-03, INV-IDX-04 | Keeper maintenance: accrues interest to the current ledger timestamp. Accrual never lowers the borrow or supply index and each chunk's rate is capped at max_borrow_rate, so the caller chooses only the accrual timing and cannot lower anyone's balance.
controller::claim_revenue | caller-auth | INV-AUTH-03, INV-ACCT-06 | Keeper maintenance: sweeps accrued protocol revenue to the governance-configured accumulator. The caller picks the timing, never the recipient.
controller::update_account_threshold | caller-auth | INV-AUTH-03, INV-RISK-01 | Keeper maintenance: restamps cached risk parameters to their currently listed values. Without has_risks it restamps LTV only, which the health factor does not read; with has_risks set it reverts unless the account clears the update health-factor floor, so it cannot be used to push an account into liquidation.
controller::flash_loan | caller-auth | INV-AUTH-03, INV-FLASH-01, INV-FLASH-02 | Anyone may borrow within a single call; the pool verifies principal plus fee is back before returning, and the flash-loan flag blocks monetary reentrancy into position flows.
```

**File:** contracts/pool/README.md (L139-155)
```markdown
| `supply` | `AmountMustBePositive` (14) on a negative amount, `PoolInsolvent` (123) when the market is under-backed, `SupplyRoundsToZeroShares` (51) |
| `borrow` | `AmountMustBePositive` (14) — zero is rejected here, `InsufficientLiquidity` (112) from cash or the liquidation buffer, `BorrowRoundsToZeroShares` (47), `UtilizationAboveMax` (127) |
| `withdraw` | `AmountMustBePositive` (14) on a negative amount or fee, `WithdrawRoundsToZeroShares` (49), `WithdrawLessThanFee` (115), `InsufficientLiquidity` (112), `UtilizationAboveMax` (127) on non-liquidation calls, `PoolInsolvent` (123), `InternalError` (34) |
| `repay` | `AmountMustBePositive` (14), `RepayRoundsToZeroShares` (52), `MathOverflow` (33) |
| `net_settle` | `AmountMustBePositive` (14), `NetSettleRoundsToZeroShares` (50), `PoolInsolvent` (123), `InternalError` (34) |
| `seize_positions` | `AmountMustBePositive` (14), `InternalError` (34) |
| `flash_loan` | `AmountMustBePositive` (14), `FlashloanNotEnabled` (401), `InsufficientLiquidity` (112), `InvalidFlashloanReceiver` (412) for a non-Wasm receiver, `InvalidFlashloanRepay` (402) for a short allowance or a balance mismatch |
| `create_strategy` | `AmountMustBePositive` (14) on a negative amount, `StrategyFeeExceeds` (409), plus the whole `borrow` set — it mints debt through the same path |
| `recapitalize` | `AmountMustBePositive` (14) on a negative amount, `MathOverflow` (33) |
| `claim_revenue` | `UtilizationAboveMax` (127), `PoolInsolvent` (123), `OwnerNotSet` (32), `InternalError` (34) |
| `upgrade` | none beyond the owner check |

Every market entrypoint also panics with `PoolNotInitialized` (30) when the
market does not exist, and with `MathOverflow` (33) on a checked-arithmetic
overflow. `InternalError` (34) marks a broken invariant: `revenue > supplied`
after a supply burn or a deposit seizure, or a revenue claim that burns zero
shares.
```

**File:** contracts/controller/src/external/pool.rs (L158-165)
```rust
/// Accrues interest, then replaces the rate model and flash-loan settings.
pub(crate) fn pool_update_params_call(
    env: &Env,
    pool_addr: &Address,
    hub_asset: &HubAssetKey,
    params: &InterestRateModel,
) {
    LiquidityPoolClient::new(env, pool_addr).update_params(hub_asset, params)
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L26-38)
```rust
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-333)
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
