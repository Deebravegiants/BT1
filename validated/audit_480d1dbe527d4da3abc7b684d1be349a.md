### Title
Unaccounted tokens sent directly to the liquidity pool are permanently locked - (File: contracts/pool/src/cache/cash.rs)

### Summary
The liquidity pool tracks available reserves through its internal `cash` field rather than its actual token balance. An unprivileged user can transfer market tokens directly to the pool, but no entrypoint credits those tokens to the sender, another account, revenue, or backing shortfall. Because all outbound pool transfers are limited by internal accounting cash, the excess token balance remains permanently locked.

### Finding Description
The pool explicitly separates its accounting cash from its live token balance: `cash` is loaded from persistent market state, while `transfer_out` performs the token transfer without deriving the transferable amount from the pool's actual balance. [1](#0-0) [2](#0-1) 

Normal deposits avoid this issue because the controller calls the token contract for exactly the requested amount and passes the measured pool balance increase to `pool.supply`. [3](#0-2)  The pool then mints supply shares and credits `cash` only for that measured amount. [4](#0-3) 

However, a user can bypass the controller and invoke `token.transfer(user, pool_address, amount)` directly. That raises the pool's token balance without changing stored `cash`, `supplied`, `revenue`, or any user's position. The pool exposes mutators only to its controller owner and has no skim/rescue entrypoint. [5](#0-4)  Withdrawals must first pass the internal reserve check and then debit stored cash, so the stray balance does not become withdrawable. [6](#0-5) [7](#0-6) 

Revenue claims cannot recover it either: `claim_revenue` burns only recorded revenue shares and debits the resulting amount from stored cash. [8](#0-7)  Likewise, recapitalization credits only a measured controller prefund up to the backing shortfall and refunds the remainder rather than recognizing pre-existing pool balance. [9](#0-8) [10](#0-9) 

### Impact Explanation
A user who transfers tokens directly to the pool permanently loses those tokens. The assets increase the pool's token balance but remain outside every accounting total used to authorize withdrawals, borrows, revenue claims, or recapitalization. No in-scope unprivileged path can recover the excess, and the pool itself has no sweep function.

This is a permanent freezing-of-funds issue rather than merely an accounting mismatch: the tokens remain physically held by the pool but cannot be paid out because `require_reserves` and `debit_cash` constrain payments to the internally tracked `cash` value. [6](#0-5) [7](#0-6) 

### Likelihood Explanation
Likelihood depends on a user sending tokens directly to the pool rather than through `Controller::supply`, `repay`, or `recapitalize`. The controller's normal flows measure and account for exactly the received amount, so routine usage does not trigger the issue. [11](#0-10) 

Nevertheless, the pool address is public and direct token transfers are permissionless. User interfaces, integrations, or users can reasonably transfer to the pool address expecting it to count as a deposit or recapitalization. Once sent, there is no recovery path.

### Recommendation
Add an owner-controlled rescue/skim operation for each market that computes:

```rust
stranded = token.balance(pool) - cash
```

and transfers only the positive `stranded` amount to a configured recovery address. The function must reject tokens for which actual balance is less than accounting cash so it cannot consume reserves backing positions.

Alternatively, add a permissionless reconciliation operation that credits a genuine accidental transfer to `cash` only when doing so cannot mint shares or create claims—for example, by treating it as recapitalization up to the backing shortfall and retaining only a separately tracked donation balance. A direct transfer should not be silently incorporated into supplier backing in a way that changes existing share exchange rates.

### Proof of Concept
1. Deploy and configure a market with accounting state `cash = C` and pool token balance `B >= C`.
2. An unprivileged user calls `token.transfer(user, pool_address, X)` directly for `X > 0`.
3. The pool token balance becomes `B + X`, while stored market `cash` remains `C` because no pool function was invoked. [12](#0-11) 
4. Withdrawals and borrows remain limited to `cash`; `claim_revenue` is limited to recorded revenue shares; and `recapitalize` examines only the newly measured prefund, not the pre-existing surplus. [8](#0-7) [13](#0-12) 
5. Since `transfer_out` is private to pool operations and every mutator is controller-owner gated, the user cannot cause the pool to transfer out the additional `X`. [14](#0-13) [15](#0-14) 
6. Result: `X` remains permanently frozen as an unaccounted pool balance.

### Citations

**File:** contracts/pool/src/cache/mod.rs (L49-70)
```rust
    pub(crate) fn load(env: &Env, hub_asset: &HubAssetKey) -> Self {
        let raw_params = storage::read_params(env, hub_asset);
        let raw_state = storage::read_state(env, hub_asset);
        storage::renew_market(env, hub_asset);

        let state = PoolState::from(&raw_state);
        let params = MarketParams::from(&raw_params);
        let time = time::now_ms(env);

        Self {
            env: env.clone(),
            hub_asset: hub_asset.clone(),
            params,
            last_timestamp: state.last_timestamp,
            current_timestamp: time,
            supplied: state.supplied,
            borrowed: state.borrowed,
            revenue: state.revenue,
            borrow_index: state.borrow_index,
            supply_index: state.supply_index,
            cash: state.cash,
        }
```

**File:** contracts/pool/src/cache/mod.rs (L128-131)
```rust
    /// Cash reserves in asset units (accounting book, not live token balance).
    pub(crate) fn cash(&self) -> i128 {
        self.cash
    }
```

**File:** contracts/pool/src/cache/cash.rs (L14-20)
```rust
    /// Panics if cash reserves are below `amount`.
    pub(crate) fn require_reserves(&self, amount: i128) {
        assert_with_error!(
            self.env,
            self.cash >= amount,
            CollateralError::InsufficientLiquidity
        );
```

**File:** contracts/pool/src/cache/cash.rs (L34-40)
```rust
    pub(crate) fn debit_cash(&mut self, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        self.require_reserves(amount);
        self.cash = self
            .cash
            .checked_sub(amount)
            .unwrap_or_else(|| panic_with_error!(&self.env, GenericError::MathOverflow));
```

**File:** contracts/pool/src/cache/cash.rs (L43-52)
```rust
    /// Transfers `amount` of the market asset from the pool to `recipient`.
    ///
    /// Rejects negative amounts; zero is a no-op. Does not adjust accounting cash.
    pub(crate) fn transfer_out(&self, recipient: &Address, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        if amount == 0 {
            return;
        }
        let tok = token::Client::new(&self.env, &self.params.asset_id);
        tok.transfer(&self.env.current_contract_address(), recipient, &amount);
```

**File:** contracts/controller/src/positions/supply.rs (L116-129)
```rust
    for (hub_asset, amount_in) in aggregated.iter() {
        let asset_config: AssetConfig = cache.require_spoke_asset(account.spoke_id, &hub_asset);
        let received = payments::transfer_amount_measured(
            env,
            &hub_asset.asset,
            caller,
            &pool_addr,
            amount_in,
            GenericError::AmountMustBePositive,
        );
        let position = account.get_or_create_supply_position(&hub_asset, &asset_config);
        entries.push_back(PoolSupplyEntry {
            action: make_pool_action(&position, received, hub_asset.clone()),
        });
```

**File:** contracts/pool/src/ops/supply.rs (L23-40)
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

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/lib.rs (L31-37)
```rust
//! ## Security notes
//!
//! - Every mutator requires the owner through `#[only_owner]`; views are public.
//! - Cash is an accounting book, separate from the token balance. A flash loan
//!   checks the token balance after payout, after the callback and after
//!   repayment.
//! - Write paths extend the instance TTL. Every market load, views included,
```

**File:** contracts/pool/src/lib.rs (L128-133)
```rust
    /// Accrues, mints scaled supply shares and credits cash per entry. The
    /// controller transfers the tokens in before this call. Owner-only.
    #[only_owner]
    fn supply(env: Env, entries: Vec<PoolSupplyEntry>) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, ops::supply::apply)
    }
```

**File:** contracts/pool/src/ops/revenue.rs (L39-47)
```rust
pub(crate) fn accounting(env: &Env, hub_asset: HubAssetKey) -> RevenueOutcome {
    let mut cache = ops::renewed_market(env, &hub_asset);

    let net_transfer = cache.burn_claimable_revenue();

    guards::require_utilization_below_max(env, &cache);
    guards::require_supply_for_debt(env, &cache);
    cache.debit_cash(net_transfer);

```

**File:** contracts/controller/src/markets.rs (L151-163)
```rust
    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    // Prefund the pool and credit only its measured receipt.
    let received = payments::transfer_amount_measured(
        env,
        &hub_asset.asset,
        &payer,
        &pool_addr,
        amount,
        GenericError::AmountMustBePositive,
    );

    pool_recapitalize_call(env, &pool_addr, &hub_asset, &payer, received).actual_amount
```

**File:** contracts/pool/src/ops/recapitalize.rs (L49-58)
```rust
    require_nonneg_amount(env, amount);
    let mut cache = ops::renewed_market(env, &hub_asset);

    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();
```

**File:** common/src/token.rs (L16-30)
```rust
pub fn transfer_amount_measured(
    env: &Env,
    asset: &Address,
    from: &Address,
    to: &Address,
    amount: i128,
    non_positive_error: GenericError,
) -> i128 {
    assert_with_error!(env, amount > 0, non_positive_error);
    let tok = token::Client::new(env, asset);
    let pre = tok.balance(to);
    tok.transfer(from, to, &amount);
    let post = tok.balance(to);
    post.checked_sub(pre)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::AmountMustBePositive))
```
