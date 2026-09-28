### Title
Market accrual overflows before the borrow-index cap, permanently freezing repayment and withdrawals - ([File: common/src/rates/simulate.rs](https://github.com/AYontt/rs-lending-xlm--021/blob/main/common/src/rates/simulate.rs))

### Summary
A sufficiently large borrowed position can make `borrowed * borrow_index` overflow before `borrow_index` reaches `MAX_BORROW_INDEX_RAY`. [1](#0-0) [2](#0-1)  Because every market mutation accrues first, one overflowing accrual permanently blocks `withdraw`, `repay`, `borrow`, `supply`, liquidation-related pool calls, and later `update_indexes` calls for that market. [3](#0-2) [4](#0-3) 

### Finding Description
`accrue_step` converts the scaled borrowed balance to underlying value using `scaled_to_original`, which performs checked RAY multiplication and panics on `i128` overflow. [5](#0-4) [6](#0-5)  The borrow index is capped only after this debt valuation, so the cap cannot prevent an oversized book from overflowing during accrual. [2](#0-1)  `global_sync` invokes this step for every elapsed chunk before it marks the market accrued, leaving `last_timestamp` behind when the multiplication traps. [7](#0-6) [8](#0-7)  The regression test demonstrates a market whose index remains below `MAX_BORROW_INDEX_RAY` but whose next accrual returns `MathOverflow`, after which withdrawals and repayments fail identically. [9](#0-8) 

An attacker can reach the state through ordinary `controller.supply` and `controller.borrow` flows if the spoke caps, available collateral, token supply, and utilization configuration permit a sufficiently large debt book. [10](#0-9) [11](#0-10)  Once enough time has passed, any address may trigger the fatal accrual through `controller.update_indexes(caller, assets)`, which authenticates only `caller` and forwards the selected `HubAssetKey` list to the pool. [12](#0-11) [13](#0-12) 

### Impact Explanation
The impact is permanent freezing of user funds and protocol insolvency handling for the affected market: suppliers cannot withdraw, borrowers cannot repay, new rescue liquidity cannot be supplied, and liquidations or bad-debt operations cannot execute because all of those paths load and accrue the same market first. [14](#0-13) [15](#0-14)  Since the failing arithmetic occurs before state commit and `last_timestamp` is not advanced, waiting or retrying does not repair the market. [16](#0-15) 

### Likelihood Explanation
Likelihood is constrained by the very large value required for `borrowed_scaled_ray * borrow_index` to exceed the RAY-domain `i128` range, and by market caps, collateral requirements, cash availability, and utilization limits. [17](#0-16) [18](#0-17)  Nevertheless, no invariant prevents a high-decimal, high-cap market from entering this range, and the repository’s regression test reaches the condition through public supply and borrow actions at sustained high utilization. [19](#0-18) 

### Recommendation
Compute utilization without materializing an unbounded `borrowed * index` value, for example by using a wider intermediate, saturating utilization, or checking `borrowed > i128::MAX / index` before multiplication. [20](#0-19)  Apply the same protection to supplied-value and reward calculations, then advance or bound accrual state so oversized books degrade gracefully instead of poisoning every future market operation. [21](#0-20) [16](#0-15) 

### Proof of Concept
1. Through `controller.supply`, deposit a large amount of a high-decimal debt-market asset and a second collateral asset under the same unprivileged account. [22](#0-21) 
2. Through `controller.borrow`, borrow a large fraction of the debt-market liquidity, producing a large scaled `borrowed` balance. [23](#0-22) 
3. Let the borrow index compound at high utilization until `borrowed * borrow_index` exceeds the representable RAY value while `borrow_index` is still below `MAX_BORROW_INDEX_RAY`. [20](#0-19) [24](#0-23) 
4. Call `controller.update_indexes(caller, vec![market_key])`; the call traps with `MathOverflow`. [12](#0-11) [25](#0-24) 
5. Subsequent `withdraw` and `repay` calls also fail with `MathOverflow`, proving that the market cannot recover through ordinary user actions. [15](#0-14)

### Citations

**File:** common/src/rates/simulate.rs (L51-66)
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

**File:** contracts/pool/README.md (L157-168)
```markdown
## Flow

Each mutation of an existing market runs this sequence:

```text
entrypoint (#[only_owner])
  → Cache::load             # read params + state, bump TTL
  → interest::global_sync   # accrue to now, in ≤1yr chunks
  → mutate                  # cache/shares.rs, cache/cash.rs
  → guards::*               # reserve, utilization, backing checks
  → commit → transfer_out → emit
```
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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }
```

**File:** contracts/pool/src/lib.rs (L128-147)
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

**File:** docs/explanation/threat-model.md (L317-324)
```markdown
## Numeric and resource limits

Finite RAY value capacity can be exhausted before the index ceiling. Synchronizing
an overlarge book can then fail before an otherwise risk-reducing operation.
Caps must account for plausible index growth as well as token balances.
Accrual cadence changes utilization and subsequent rates; bounded chunks do not
make cadence neutral or prove exact conservation after integer rounding.
See [numeric limits](../reference/formulas.md#numeric-limits).
```

**File:** skills/xoxno-lending/math.md (L435-447)
```markdown
## Caps in the scaled domain

`SpokeAssetConfig.supply_cap` / `borrow_cap` are token base units per spoke and always enforced (`0` = closed side; no unlimited sentinel; `i128::MAX` rejected at config time). Entry (`contracts/controller/src/spoke_usage.rs::enforce_spoke_cap`) compares shares:

```text
cap_scaled     = floor_saturating(cap × 10^(27−d) × RAY / index)      // calculate_scaled_cap, supply or borrow index
usage_scaled   = SpokeUsageRaw.supplied_scaled_ray | borrowed_scaled_ray   // get_spoke_usage
usage + new_shares ≤ cap_scaled   else SpokeSupplyCapReached | SpokeBorrowCapReached
headroom_tokens = floor(floor((cap_scaled − usage) × index / RAY) / 10^(27−d))
```

Exits subtract usage without checking caps. Cap conversion saturates at `i128::MAX`; the admitted cap maximum is `i128::MAX / 10^(27−d)` (`max_cap_for_decimals`).

```
