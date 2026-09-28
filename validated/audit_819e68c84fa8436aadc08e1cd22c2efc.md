### Title
Unchecked RAY-value multiplication permanently freezes an oversized high-utilization market - (File: `common/src/rates/scaling.rs`)

### Summary
An unprivileged borrower can leave an extremely large market at sustained high utilization until `borrowed_shares * borrow_index` exceeds `i128`, after which every state-changing market path reverts during mandatory interest accrual. The borrow index is capped, but the unbounded debt-value multiplication occurs before the cap can protect subsequent accruals, freezing supplier withdrawals, borrower repayments, liquidations, revenue claims, and recapitalization for that market. [1](#0-0) [2](#0-1) 

### Finding Description
Users reach the vulnerable state through `controller.supply`, `controller.borrow`, and the permissionless `controller.update_indexes` entrypoints. [3](#0-2) [4](#0-3) 

Each pool mutation loads the market and runs `global_sync` before applying the operation, while `update_indexes` invokes the same accrual loop for every requested market. [5](#0-4) [6](#0-5) 

`accrue_step` first converts stored scaled debt and scaled supply back to RAY-denominated values through `scaled_to_original`. [7](#0-6) 

`scaled_to_original` performs the raw `scaled * index` multiplication, so a sufficiently large `borrowed` share balance and accumulated `borrow_index` exceed the `i128` value domain and panic with `MathOverflow`. [8](#0-7) 

Although `update_borrow_index` clamps the next index to `MAX_BORROW_INDEX_RAY`, that check occurs only after the current debt value has already been multiplied inside the accrual step. [2](#0-1) [9](#0-8) 

Because supply mints debt through the same sync-and-mutate flow, and borrow enforces reserves before minting, ordinary user operations can construct the oversized supplied/borrowed totals when the listed market caps permit them. [10](#0-9) [11](#0-10) 

### Impact Explanation
Once the stored `borrowed * borrow_index` product exceeds the `i128` domain, every operation that accrues that market reverts before its state transition executes. [6](#0-5) [12](#0-11) 

This indefinitely freezes supplier withdrawals and protocol revenue, prevents debt repayment and liquidation, and can leave pool cash inaccessible even when the pool contract is solvent. [13](#0-12) 

The controller’s owner-facing pool maintenance path is also ineffective for lowering utilization because replacing the rate model commits a synced market before writing the new model. [14](#0-13) 

Recovery would require a contract upgrade or other out-of-band code migration, so the in-scope impact is at minimum prolonged freezing of user funds and can be permanent if no compatible upgrade is deployed. [15](#0-14) 

### Likelihood Explanation
The attack requires a market configuration whose asset caps permit a scaled book large enough that index growth can push the underlying RAY value beyond `i128`, plus enough attacker liquidity to hold utilization near the high-rate segment. [11](#0-10) [8](#0-7) 

Those are demanding capital and configuration prerequisites, but they do not require privileged authorization, malformed parameters, leaked keys, oracle manipulation, or a third-party contract failure. [3](#0-2) [4](#0-3) 

The resulting failure is deterministic rather than a budget or memory limitation: state growth makes the required fixed-point value unrepresentable, so future transactions keep failing regardless of how much compute the caller supplies. [1](#0-0) [8](#0-7) 

### Recommendation
Constrain market supply and borrow caps so `scaled_shares * MAX_INDEX` remains inside the supported RAY value domain, and enforce those bounds against both current and future index growth. Use widened arithmetic or saturating debt-value calculations inside `accrue_step`, cap debt growth before unbounded multiplication, and provide an explicit terminal state that still permits repayments, collateral liquidation, and supplier exits after the index ceiling is reached. [16](#0-15) [2](#0-1) 

### Proof of Concept
For a listed target market `T` and a collateral market `C`, with caps and collateral value sufficient to borrow approximately `0.98 * T_supply`:

```rust
let liquidity_account = controller.supply(
    attacker,
    0,
    spoke_id,
    vec![(T, whale_supply)],
);

let borrower_account = controller.supply(
    attacker,
    0,
    spoke_id,
    vec![(C, sufficient_collateral)],
);

controller.borrow(
    attacker,
    borrower_account,
    vec![(T, whale_supply * 98 / 100)],
    Some(attacker),
);
```

After enough time passes at that utilization, call:

```rust
controller.update_indexes(attacker, vec![T]);
```

The next accrual computes `borrowed * borrow_index` through `scaled_to_original` before the index cap can provide protection, causing `MathOverflow`. [12](#0-11) [8](#0-7) 

Subsequent `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `recapitalize`, `claim_revenue`, or further `update_indexes` calls for `T` enter the same mandatory accrual path and revert at the same multiplication. [5](#0-4) [6](#0-5)

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

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L80-83)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);
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

**File:** contracts/controller/src/lib.rs (L367-371)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
```

**File:** contracts/pool/src/ops/market.rs (L52-57)
```rust
pub(crate) fn replace_rate_model(env: &Env, hub_asset: HubAssetKey, model: InterestRateModel) {
    ops::renewed_market(env, &hub_asset).commit();

    let params = storage::write_rate_model(env, &hub_asset, &model);
    params.verify(env);
    events::emit_market_params(env, hub_asset.hub_id, hub_asset.asset, params);
```

**File:** contracts/pool/src/ops/market.rs (L65-72)
```rust
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
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

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** contracts/pool/src/ops/borrow.rs (L63-78)
```rust
pub(crate) fn mint_debt(env: &Env, cache: &mut Cache, position: &mut Ray, amount: i128) {
    require_positive_amount(env, amount);
    cache.require_reserves(amount);
    guards::require_liquidation_buffer(env, cache, amount);

    let minted = cache.calculate_scaled_borrow(amount);

    assert_with_error!(
        env,
        minted.raw() > 0,
        GenericError::BorrowRoundsToZeroShares
    );

    *position = position.checked_add(env, minted);
    cache.mint_debt(minted);
    guards::require_utilization_below_max(env, cache);
```

**File:** contracts/pool/src/lib.rs (L119-126)
```rust
    /// Upgrades the contract WASM to `new_wasm_hash`, extending instance TTL
    /// first. Restricted to the owner.
    #[only_owner]
    fn upgrade(env: Env, new_wasm_hash: BytesN<32>) {
        renew_instance(&env);
        env.deployer()
            .update_current_contract(ContractExecutable::Wasm(new_wasm_hash));
    }
```

**File:** contracts/pool/src/lib.rs (L128-180)
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
    }
```
