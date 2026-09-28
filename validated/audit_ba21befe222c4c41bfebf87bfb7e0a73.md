### Title
Unchecked aggregate accrual overflow permanently freezes market operations - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary
A sufficiently large market can reach a state where unscaling aggregate debt or supply overflows `i128`, causing every subsequent accrual-dependent operation on that market to revert with `MathOverflow`. [1](#0-0) [2](#0-1) 

### Finding Description
`accrue_step` converts the total scaled debt and supply into their present values before calculating utilization and interest. [3](#0-2)  The conversion delegates to `scaled.mul(env, index)`, which panics when the resulting aggregate `Ray` value exceeds `i128`. [4](#0-3)  The borrow-index ceiling only caps `old_index * interest_factor`; it does not bound `borrowed * borrow_index` or `supplied * supply_index`. [5](#0-4)  Consequently, a large admitted scaled balance can overflow the aggregate value well before the index itself reaches `MAX_BORROW_INDEX_RAY`. [6](#0-5) 

Every pool market mutation loads its cache through `synced_market`, which unconditionally calls `interest::global_sync`. [7](#0-6)  `global_sync` invokes `accrue_step` for each elapsed accrual chunk, so the overflow is reached before the requested repayment, withdrawal, liquidation, bad-debt cleanup, recapitalization, or other mutation executes. [8](#0-7)  Once the market enters this state, the reverting accrual runs before every ordinary escape path, leaving no in-contract operation to reduce the oversized scaled balances. [9](#0-8) 

### Impact Explanation
This permanently freezes all user funds associated with the affected market: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and cleanup cannot reduce the problematic position. [10](#0-9)  The protocol documentation also acknowledges that accrued values can overflow before the index ceiling and block repayment or withdrawal because those operations accrue first. [11](#0-10)  Recovery would require intervention outside the affected market’s normal accounting paths, such as a contract upgrade, so this is not merely a temporary fail-closed condition. [12](#0-11) 

### Likelihood Explanation
An unprivileged attacker can create the condition through ordinary `supply` and `borrow` calls if a market’s configured caps permit a sufficiently large scaled position and the interest-rate model produces enough index growth. [13](#0-12)  The attacker does not need malformed input, privileged access, oracle manipulation, or unsafe memory behavior; the harness demonstrates the condition using permitted raw amounts on an 18-decimal market at high utilization. [14](#0-13)  The requirement for substantial capital and compatible market parameters limits practical exploitability, but the same state can also arise organically in a large legitimate market and freezes every participant rather than only the attacker. [15](#0-14) 

### Recommendation
Enforce an aggregate-value domain bound when admitting or growing scaled supply and debt, using the protocol’s maximum possible index multiplier rather than only the current index and asset-unit cap. [16](#0-15)  Alternatively, perform aggregate accrual calculations in a wider representation such as `I256` and explicitly bound or resolve the market before any value that cannot be represented as a `Ray` is produced. [17](#0-16)  Add a permanent regression test that attempts `update_indexes`, `withdraw`, `repay`, liquidation, bad-debt cleanup, and `recapitalize` after constructing the overflow state. [18](#0-17) 

### Proof of Concept
The repository already contains a deterministic reproduction in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`. [14](#0-13) 

```text
1. Configure an 18-decimal target market with caps lifted to the admitted domain maximum.
2. The attacker calls Controller.supply with:
   account_id = 0
   assets = [(target_hub_asset, 1_000_000_000 * 10^18)]
3. The attacker supplies sufficient collateral in another listed market and calls:
   Controller.borrow(
     account_id,
     borrows = [(target_hub_asset, 98 * 10^7 * 10^18)],
     to = None
   )
4. Advance ledger time while utilization remains high.
5. Call Controller.update_indexes([target_hub_asset]).
   Result: MathOverflow while the borrow index is still below MAX_BORROW_INDEX_RAY.
6. Call Controller.withdraw(account_id, [(target_hub_asset, 1)], None).
   Result: MathOverflow before withdrawal logic.
7. Call Controller.repay(account_id, [(target_hub_asset, small_amount)]).
   Result: MathOverflow before repayment logic.
```

The test asserts `MathOverflow` on index update and confirms that both withdrawal and repayment subsequently fail with the same error. [18](#0-17)

### Citations

**File:** common/src/rates/simulate.rs (L51-64)
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-319)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L342-356)
```rust
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

**File:** common/src/rates/scaling.rs (L35-56)
```rust
/// Converts an asset-unit `amount` to a scaled supply `Ray` using floor
/// rounding relative to `supply_index`.
pub fn calculate_scaled_supply(env: &Env, amount: i128, decimals: u32, supply_index: Ray) -> Ray {
    Ray::from_asset(env, amount, decimals).div_floor(env, supply_index)
}

/// Converts an asset-unit `amount` to a scaled supply `Ray` using ceiling
/// rounding relative to `supply_index`.
pub fn calculate_scaled_supply_ceil(
    env: &Env,
    amount: i128,
    decimals: u32,
    supply_index: Ray,
) -> Ray {
    Ray::from_asset(env, amount, decimals).div_ceil(env, supply_index)
}

/// Converts an asset-unit `amount` to a scaled borrow `Ray` using ceiling
/// rounding relative to `borrow_index`.
pub fn calculate_scaled_borrow(env: &Env, amount: i128, decimals: u32, borrow_index: Ray) -> Ray {
    Ray::from_asset(env, amount, decimals).div_ceil(env, borrow_index)
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

**File:** contracts/pool/src/ops/mod.rs (L29-39)
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

**File:** contracts/controller/src/spoke_usage.rs (L100-114)
```rust
    /// Buffers a scaled increase from stored usage, or zero for a missing row.
    /// Rejects totals above the cap converted at the supplied index.
    pub(crate) fn apply_entry(
        &mut self,
        side: UsageSide,
        hub_asset: &HubAssetKey,
        delta_scaled: Ray,
        cap: i128,
        index: Ray,
        decimals: u32,
    ) {
        let mut usage = self.load_usage_row(hub_asset).unwrap_or_default();
        let next = enforce_spoke_cap(&self.env, side, &usage, delta_scaled, cap, index, decimals);
        side.set_scaled(&mut usage, next.raw());
        self.usage.set(hub_asset.clone(), usage);
```

**File:** common/src/math/fp_core.rs (L14-20)
```rust
/// Widens `x`, `y`, and `d` to `I256` for overflow-safe intermediate arithmetic.
fn to_i256_operands(env: &Env, x: i128, y: i128, d: i128) -> (I256, I256, I256) {
    (
        I256::from_i128(env, x),
        I256::from_i128(env, y),
        I256::from_i128(env, d),
    )
```
