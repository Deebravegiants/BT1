### Title
Protocol revenue can be claimed while the market remains under-backed - ([File: contracts/pool/src/ops/revenue.rs](contracts/pool/src/ops/revenue.rs))

### Summary
`supply` rejects an under-backed market through `require_backed_market`, but `claim_revenue` does not repeat that solvency check. After bad-debt socialization leaves a shortfall because the supply index reaches `SUPPLY_INDEX_FLOOR_RAW`, any caller can trigger revenue withdrawal while supplier claims still exceed cash plus debt. Revenue is routed to the configured accumulator rather than the caller, but the withdrawal still consumes scarce pool backing ahead of impaired suppliers.

### Finding Description
The pool defines backing shortfall as floored supplier claims minus cash plus ceiled outstanding debt [1](#0-0) . `require_backed_market` requires that shortfall to be zero [2](#0-1) , but it is applied only on `supply` [3](#0-2) .

The documented guard matrix shows that `claim_revenue` runs `require_reserves`, `require_utilization_below_max`, and `require_supply_for_debt`, while `require_backed_market` runs only on `supply` [4](#0-3) . `require_supply_for_debt` only rejects the narrower case where all supply is gone while debt remains; it does not detect a positive backing shortfall [5](#0-4) .

Bad-debt cleanup can create the required precondition without privileged access: the supply index is written down only to `SUPPLY_INDEX_FLOOR_RAW`, and the documented design explicitly says liquidation and cleanup have no final full-backing assertion, so the index floor can leave a shortfall [6](#0-5) . Once that state exists, the permissionless controller `claim_revenue` path calls the pool and forwards measured receipts to the accumulator [7](#0-6) [8](#0-7) .

### Impact Explanation
Revenue shares are part of `supplied`, so converting them into a cash withdrawal while `backing_shortfall > 0` takes assets that should first cover existing supplier claims. This can increase the market shortfall and permanently impair suppliers unless someone later recapitalizes the market. New supply remains blocked by `require_backed_market`, while revenue extraction remains available, making this a missing post-state solvency check rather than a validation asymmetry that protects exit liquidity.

### Likelihood Explanation
The setup is reachable by an unprivileged caller through `clean_bad_debt` once an account has debt greater than collateral and collateral is at or below the dust threshold. The supply-index floor means socializing the loss can terminate before supplier claims are fully written down. `claim_revenue` is then callable by any authenticated address; authorization only prevents callback-style flash-loan reentry and does not require ownership [9](#0-8) .

### Recommendation
Apply `require_backed_market` after burning revenue shares and before debiting cash in the pool’s `claim_revenue` operation, or make revenue claiming cap the withdrawal to the amount that preserves zero backing shortfall. The check should run after interest accrual and revenue-share mutation, not merely when the market is opened or when new supply enters.

### Proof of Concept
1. Configure a market with a nonzero reserve factor so protocol revenue exists.
2. A borrower opens a position that later becomes insolvent with collateral at or below the bad-debt dust threshold.
3. Any caller invokes `Controller::clean_bad_debt(caller, account_id)`.
4. Bad-debt socialization writes down the supply index, but `SUPPLY_INDEX_FLOOR_RAW` prevents full loss absorption and leaves `backing_shortfall(cache) > 0`.
5. Any caller invokes `Controller::claim_revenue(caller, vec![hub_asset])`.
6. The pool accepts the claim because it checks reserves, utilization, and nonzero supply-with-debt, but not `require_backed_market`.
7. Revenue cash is transferred onward to the accumulator while supplier claims remain under-backed; subsequent supply still reverts with `PoolInsolvent`, confirming that the market was already in a state where backing was supposed to matter.

### Citations

**File:** contracts/pool/src/guards.rs (L49-57)
```rust
/// Panics with `PoolInsolvent` if the market has a positive backing shortfall.
///
/// Backing = cash + ceiled debt value; claims = floored supply value.
pub(crate) fn require_backed_market(env: &Env, cache: &Cache) {
    assert_with_error!(
        env,
        backing_shortfall(cache) == 0,
        CollateralError::PoolInsolvent
    );
```

**File:** contracts/pool/src/guards.rs (L60-66)
```rust
/// Asset units by which supplier claims exceed cash + debt (0 if solvent).
pub(crate) fn backing_shortfall(cache: &Cache) -> i128 {
    let supplied_claim = cache.unscale_supply_floor(cache.supplied());
    let outstanding_debt = cache.unscale_borrow_ceil(cache.borrowed());
    let backing = cache.cash().saturating_add(outstanding_debt);
    supplied_claim.saturating_sub(backing).max(0)
}
```

**File:** contracts/pool/src/guards.rs (L68-72)
```rust
/// Panics with `PoolInsolvent` if supplied is zero while borrowed debt is non-zero.
pub(crate) fn require_supply_for_debt(env: &Env, cache: &Cache) {
    if cache.supplied() == Ray::ZERO && cache.borrowed() != Ray::ZERO {
        panic_with_error!(env, CollateralError::PoolInsolvent);
    }
```

**File:** contracts/pool/src/ops/supply.rs (L23-38)
```rust
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    guards::require_backed_market(env, &cache);

    let minted = cache.calculate_scaled_supply(amount);
    assert_with_error!(
        env,
        amount == 0 || minted.raw() > 0,
        GenericError::SupplyRoundsToZeroShares
    );

    position = position.checked_add(env, minted);
    cache.mint_supply(minted);

    cache.credit_cash(amount);
```

**File:** contracts/pool/README.md (L261-273)
```markdown
## Guards

Four guards live in `guards.rs`; `require_reserves` is a `Cache` method in
`cache/cash.rs`. `create_strategy` mints debt through `borrow::mint_debt`, so it
inherits every guard that `borrow` runs.

| Guard | Fires on | Not on | Error |
| --- | --- | --- | --- |
| `require_backed_market` | `supply` | everything else | `PoolInsolvent` (123) |
| `require_reserves` | `borrow`, `create_strategy`, `withdraw`, `flash_loan`, `claim_revenue` | — | `InsufficientLiquidity` (112) |
| `require_liquidation_buffer` | `borrow`, `create_strategy` | `withdraw`, `flash_loan` | `InsufficientLiquidity` (112) |
| `require_utilization_below_max` | `borrow`, `create_strategy`, `withdraw` (non-liq), `claim_revenue` | `net_settle`, `seize`, liquidation | `UtilizationAboveMax` (127) |
| `require_supply_for_debt` | `withdraw`, `net_settle`, `claim_revenue` | — | `PoolInsolvent` (123) |
```

**File:** docs/reference/invariants.md (L463-479)
```markdown
### INV-LIQ-04 — Bad-debt socialization is explicit and total

Permissionless cleanup requires ceil risk debt greater than half-up unweighted
collateral and collateral at or below the fixed $5 dust threshold. Owner-only
forced cleanup omits the dust cap. Both require debt, readable account and NFT
state, valid required prices and no active flash guard. Listing flags and
global pause do not block standalone cleanup.

Cleanup reclassifies all remaining collateral shares as revenue and writes off
all remaining debt against each debt's market. It releases spoke usage and
atomically removes account entries and the NFT. It does not net same-market
supply against debt. Standalone cleanup emits `CleanBadDebtEvent` with
pre-cleanup USD totals, without a controller position-update batch.

Ordinary liquidation and cleanup apply no final account-health or full-backing
assertion. The index floor can leave a shortfall. Recapitalization fills that
shortfall without restoring the lost index or deleted account.
```

**File:** contracts/controller/src/markets.rs (L127-136)
```rust
/// Claims and forwards revenue to the accumulator in input order. Returns
/// measured controller receipts; requires caller authorization and no flash loan.
pub(crate) fn claim_revenue(env: &Env, caller: Address, assets: Vec<HubAssetKey>) -> Vec<i128> {
    validation::require_authorized_caller(env, &caller);
    let mut results = Vec::new(env);
    let mut cache = Context::new(env);
    for hub_asset in assets {
        let amount = claim_revenue_for_asset(env, &caller, &hub_asset, &mut cache);
        results.push_back(amount);
    }
```

**File:** contracts/controller/src/markets.rs (L168-196)
```rust
fn claim_revenue_for_asset(
    env: &Env,
    caller: &Address,
    hub_asset: &HubAssetKey,
    cache: &mut Context,
) -> i128 {
    let accumulator = storage::try_get_accumulator(env)
        .unwrap_or_else(|| panic_with_error!(env, OracleError::NoAccumulator));

    let pool_addr = cache.cached_pool_address();

    // Measure custody receipts before forwarding inexact-delivery tokens (INV-ACCT-03).
    let controller = env.current_contract_address();
    let asset = &hub_asset.asset;
    let before = token::Client::new(env, asset).balance(&controller);

    let _ = pool_claim_revenue_call(env, &pool_addr, hub_asset);

    let received = balance_delta_since(env, asset, &controller, before);

    if received > 0 {
        payments::transfer_amount_measured(
            env,
            asset,
            &controller,
            &accumulator,
            received,
            GenericError::AmountMustBePositive,
        );
```

**File:** contracts/controller/src/lib.rs (L374-380)
```rust
    /// Claims pool revenue and forwards measured receipts to the accumulator.
    /// Returns those amounts in asset units, in input order. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn claim_revenue(env: Env, caller: Address, assets: Vec<HubAssetKey>) -> Vec<i128> {
        markets::claim_revenue(&env, caller, assets)
    }
```
