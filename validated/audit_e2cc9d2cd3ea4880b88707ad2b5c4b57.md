### Title
Accrual arithmetic overflow permanently freezes a high-value market - (File: `common/src/rates/scaling.rs`)

### Summary
The market accrual path unscales total debt and supply through `scaled_to_original` before applying the borrow-index ceiling. Once the scaled principal multiplied by its index no longer fits the protocol's `i128` fixed-point domain, the multiplication panics with `MathOverflow`; every subsequent market operation that accrues first reaches the same panic, permanently freezing repayment, withdrawal, liquidation, and index updates for that market. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`global_sync` executes `accrue_step` for each elapsed accrual chunk before processing a market operation. [4](#0-3) [5](#0-4) 

`accrue_step` first computes `borrowed * borrow_index` and `supplied * supply_index` through `scaled_to_original`. [6](#0-5) [1](#0-0) 

`Ray::mul` delegates to fixed-point multiply-divide arithmetic, and unrepresentable results raise `MathOverflow` rather than saturating. [7](#0-6) [8](#0-7) 

The borrow-index cap is enforced only after `old_index * interest_factor`, and it does not bound the earlier `borrowed * old_index` or `supplied * supply_index` products. [3](#0-2) [2](#0-1) 

An unprivileged user can create and fund an account through `supply`, borrow through `borrow`, and later submit `update_indexes`; repayments, withdrawals, and liquidations then traverse the same accrual-first path. [9](#0-8) [10](#0-9) [11](#0-10) [12](#0-11) 

### Impact Explanation
Once the market crosses the representable RAY-value boundary, `update_indexes` fails before committing a new accrual state, and subsequent repayment, withdrawal, or liquidation attempts fail at the same multiplication. [13](#0-12) 

This is permanent freezing of user funds rather than a transaction-local denial of service: suppliers cannot exit, borrowers cannot repay, liquidators cannot restore account health, and the market cannot resume normal operation through the affected public entrypoints. [14](#0-13) [15](#0-14) 

### Likelihood Explanation
The condition is state-dependent and requires a very large scaled balance plus sustained index growth, so it is not triggerable from an empty or ordinary market. [16](#0-15) 

Nevertheless, the path is permissionless: a sufficiently funded account can establish the large supply and borrow positions, and any caller can later submit the accrual transaction that crosses the boundary. [9](#0-8) [17](#0-16) 

The repository's dedicated stress test demonstrates that the cliff can occur before `MAX_BORROW_INDEX_RAY`, so the configured index ceiling does not prevent the freeze. [18](#0-17) 

### Recommendation
Do not expose panicking unscale operations inside mandatory accrual.

- Bound `borrowed * borrow_index` and `supplied * supply_index` before multiplication, using a market-specific maximum index derived from the stored scaled amounts.
- Alternatively, make total-value calculation saturate at a defined maximum RAY value so accrual can continue and repayment can reduce the oversized position.
- Apply the tighter index bound before updating `borrow_index` or `supply_index`, rather than relying on `MAX_BORROW_INDEX_RAY` after the fact.
- Add regression coverage proving that `update_indexes`, `repay`, `withdraw`, and `liquidate` remain executable when scaled principal approaches the representable-value limit.

### Proof of Concept
The repository already contains a reproducer at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321`. Its core sequence is:

```rust
// Large 18-decimal market plus collateral market.
let principal = BILLION * 10i128.pow(18);

// Same unprivileged flow shape: supply the debt asset, fund collateral,
// and borrow most of the supplied liquidity.
t.supply_raw(BOB, "BIG18", principal);
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98);

// Advance the ledger and invoke permissionless index accrual until the
// scaled value overflows.
loop {
    t.advance_time(YEAR_SECS);
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) {
        assert_contract_error(Err(e), errors::MATH_OVERFLOW);
        break;
    }
}

// The market remains frozen: both exit and repayment hit the same accrual panic.
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

The test confirms that the panic originates before the index cap engages and that withdrawal and repayment remain blocked afterward. [19](#0-18)

### Citations

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/simulate.rs (L60-67)
```rust
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

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** docs/reference/formulas.md (L20-24)
```markdown
Protocol boundaries require non-negative amounts; `Ray`, `Wad` and `Bps`
constructors do not enforce that restriction themselves. Multiply-divide uses
an `i128` fast path or an exact `I256` intermediate. Unrepresentable results
raise `MathOverflow`, except at explicit saturating sites; zero divisors raise
`DivisionByZero`.
```

**File:** contracts/controller/src/lib.rs (L90-114)
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
```

**File:** contracts/controller/src/lib.rs (L120-133)
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
```

**File:** contracts/controller/src/lib.rs (L144-164)
```rust
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-319)
```rust
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L329-356)
```rust
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
