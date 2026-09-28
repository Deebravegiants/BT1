### Title
Permanent market freeze through RAY debt-value overflow - (File: common/src/rates/index.rs)

### Summary
A whale-backed debt market can grow its scaled debt value beyond `i128::MAX` before either index reaches its configured ceiling, after which every mutating pool operation first accrues and therefore reverts in `accrue_step`/`calculate_supplier_rewards`. [1](#0-0) [2](#0-1) 

### Finding Description
The pool accrues interest at the start of supply, borrow, withdraw, repay, liquidation-related operations, and index maintenance because all externally routed state changes run through cache loading/accrual before their operation-specific accounting. [3](#0-2) 

`global_sync` calls `accrue_step` for every elapsed chunk, and that calculation multiplies `borrowed` by both the old and new borrow indexes to derive accrued interest. [4](#0-3) [5](#0-4) 

Those products use normal fixed-point multiplication rather than a bounded checked domain, so a sufficiently large scaled debt position reverts when `borrowed * index / RAY` leaves `i128`, even though `borrow_index` can still remain below `MAX_BORROW_INDEX_RAY`. [6](#0-5) [7](#0-6) 

### Impact Explanation
Once the market crosses this boundary, the failure becomes persistent because the next attempt to accrue recomputes the same overflowing debt value before any withdrawal, repayment, or liquidation accounting can proceed. [8](#0-7) [9](#0-8) 

The existing regression test demonstrates that `update_indexes`, supplier withdrawal, and borrower repayment all revert with `MathOverflow`, permanently freezing the pool cash and supplier claims unless governance replaces the contract or parameters through a privileged recovery path. [10](#0-9) 

### Likelihood Explanation
An unprivileged attacker can create the necessary state on an admitted market by supplying a very large debt asset, supplying separate collateral, and borrowing the debt asset at sustained high utilization; `Controller::supply`, `Controller::borrow`, and `Controller::update_indexes` are the reachable entrypoints. [11](#0-10) [12](#0-11) 

The prerequisite is economically extreme and depends on an admitted market configuration whose caps and utilization permit a debt book large enough for scaled-value overflow, so the practical severity is Medium rather than a generic low-cost denial of service. [13](#0-12) 

### Recommendation
Bound accrual inputs so scaled debt multiplied by `new_borrow_index` always remains representable, or catch this exact overflow and clamp accrual while still permitting debt-reducing and exit operations. [2](#0-1) 

At minimum, enforce market and spoke caps against a conservative future-index bound rather than only the token-domain maximum, and add a regression test proving repayments, withdrawals, and liquidation remain possible at the cap boundary. [14](#0-13) [15](#0-14) 

### Proof of Concept
1. Use an admitted debt market with a high-utilization rate curve and sufficient caps, then call `supply(caller, 0, spoke_id, [(debt_asset, principal)])` with a debt-market principal on the order of one billion 18-decimal tokens. [13](#0-12) 
2. Supply enough separate collateral to the same controlled account and call `borrow(caller, account_id, [(debt_asset, principal * 98 / 100)], None)` to establish sustained high utilization. [16](#0-15) [17](#0-16) 
3. Call `update_indexes` for the debt market as ledger time advances until `accrue_step` reaches a scaled debt value outside `i128`. [18](#0-17) [6](#0-5) 
4. The call returns `MathOverflow`, while the stored borrow index remains below `MAX_BORROW_INDEX_RAY`, showing that the index ceiling did not prevent the representable-value overflow. [7](#0-6) 
5. Subsequent `withdraw` and `repay` calls revert with the same error before their position logic can run, leaving supplier cash trapped in the market. [19](#0-18)

### Citations

**File:** contracts/pool/src/interest.rs (L20-48)
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
```

**File:** common/src/rates/index.rs (L73-87)
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

**File:** contracts/pool/src/lib.rs (L128-179)
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
    }

    /// Burns supply shares and transfers the underlying to `receiver`.
    /// `is_liquidation` skips the max-utilization check and may withhold a
    /// protocol fee. Owner-only; `actual_amount` is gross of that fee.
    #[only_owner]
    fn withdraw(
        env: Env,
        receiver: Address,
        is_liquidation: bool,
        entries: Vec<PoolWithdrawEntry>,
    ) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, |env, entry| {
            ops::withdraw::apply(env, &receiver, is_liquidation, entry)
        })
    }

    /// Burns scaled debt up to the repay amount, credits cash with the net
    /// repay and refunds overpayment to `payer`. Owner-only.
    #[only_owner]
    fn repay(env: Env, payer: Address, actions: Vec<PoolAction>) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, actions, |env, action| {
            ops::repay::apply(env, &payer, action)
        })
    }

    /// Accrues interest for each market in `hub_assets` through the current
    /// ledger time. Commits state even with no elapsed time to reserve the write
    /// footprint, and emits its market state event. Restricted to the owner.
    #[only_owner]
    fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>) {
        ops::market::accrue(&env, hub_assets);
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L347-356)
```rust
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

**File:** contracts/pool/src/ops/withdraw.rs (L57-65)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
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

**File:** common/src/rates/scaling.rs (L18-32)
```rust
/// Converts an asset-unit `cap` to a scaled `Ray` value, rounding down.
///
/// The division saturates at `i128::MAX` instead of panicking, so the cap check
/// fails open rather than trapping an entry path. The asset-to-RAY
/// rescale still panics on overflow; listings validate caps with
/// [`crate::validation::require_cap_within_asset_domain`]. Position accounting
/// uses [`calculate_scaled_supply`] and [`calculate_scaled_borrow`], which panic
/// on overflow.
pub fn calculate_scaled_cap(env: &Env, cap: i128, decimals: u32, index: Ray) -> Ray {
    Ray::from(fp_core::mul_div_floor_saturating(
        env,
        Ray::from_asset(env, cap, decimals).raw(),
        RAY,
        index.raw(),
    ))
```

**File:** docs/reference/formulas.md (L407-437)
```markdown
A cap is in native token units. Entry compares stored scaled usage plus the
new scaled amount with the cap floor-converted at the current index. Zero cap
allows no positive exposure. Exits subtract usage without checking caps;
missing usage rows and zero exit deltas are no-ops. Cap→scaled conversion
saturates at `i128::MAX` (`calculate_scaled_cap`), so the entry check fails
open instead of trapping. A saturated scaled cap does not enforce the
configured asset-unit limit. An admitted cap saturates only at an index below
one RAY. Only a bad-debt write-down moves the supply index below one RAY; at
its floor (`RAY / 1000`), a supply cap above 1/1000 of the admitted maximum
saturates. The borrow index never falls below one RAY, so an admitted borrow
cap cannot saturate. Position conversion still rejects overflow.

Flash-loan and charged strategy fees are half-up BPS of principal, with a
minimum of one base unit for a positive rate. Flash position has no origination
fee; see [its settlement invariant](invariants.md#inv-strat-04).

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
