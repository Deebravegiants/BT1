### Title
Direct token transfers to the pool are permanently uncredited and unrecoverable - (File: contracts/pool/src/lib.rs)

### Summary
The pool contract’s `cash` ledger is intentionally separate from its live token balance, and every state-changing pool entrypoint is restricted to the controller. Consequently, a user who transfers a supported asset directly to the pool address receives no supply shares or other claim, while no public or owner-facing recovery entrypoint can return the transfer. [1](#0-0) 

### Finding Description
`Controller::supply` first performs a measured token transfer from the caller to the pool and then calls `LiquidityPool::supply` with the measured receipt. [2](#0-1) 

The pool does not inspect or reconcile its token balance during `supply`; it trusts the amount supplied by its controller owner and only mints shares/credits `cash` for that declared amount. [3](#0-2) 

All pool mutation functions are owner-only, so an unprivileged sender cannot call a pool function to register or reclaim a direct token transfer. [4](#0-3) 

### Impact Explanation
A supported asset sent directly to the pool is excluded from the pool’s `cash` ledger and from every user’s supply position. The sender owns no claim that `withdraw` can use, and the contract exposes no rescue, sweep, or reconciliation operation for uncredited balances. The transferred funds are therefore permanently inaccessible to the sender and effectively become an uncredited donation backing other pool obligations. [5](#0-4) 

### Likelihood Explanation
Any unprivileged token holder can accidentally perform an ordinary SAC/token `transfer` directly to the pool address instead of invoking `Controller::supply`. No special privileges, race condition, malformed parameter, or privileged role is required. The probability depends on user or integrating-front-end error, but the result is immediate and irreversible.

### Recommendation
Add an explicit, permissionless rescue or reconciliation path for unsolicited pool balances, or provide a controller entrypoint that measures the pre-existing pool balance delta attributable to a caller’s direct deposit before crediting it.

At minimum, document the pool and controller addresses as unsafe direct-transfer destinations and ensure integrators always call `Controller::supply`, `Controller::repay`, or `Controller::recapitalize` rather than transferring tokens directly.

### Proof of Concept
1. Governance creates a market for `(hub_id, asset)`.
2. A victim invokes the SAC token’s `transfer(victim, pool_address, amount)` directly instead of calling `Controller::supply`.
3. The token balance of `pool_address` increases by `amount`, but the victim receives no supply position because `LiquidityPool::supply` was never called.
4. The pool’s `cash` remains unchanged because direct token transfers do not execute `Cache::credit_cash`. [6](#0-5) 
5. Calling `Controller::withdraw` cannot recover the donation because the victim has no supply shares to burn. [7](#0-6) 
6. Calling `Controller::recapitalize` does not associate the earlier transfer with the caller: it performs a new measured transfer and passes only that measured receipt to the pool. [8](#0-7)

### Citations

**File:** contracts/pool/src/lib.rs (L23-35)
```rust
//! ## Accounting model
//!
//! The pool stores market totals as scaled shares (RAY); the controller stores
//! the positions (INV-ACCT-10). Token amounts convert through the market's
//! supply or borrow index. Accrual raises the indexes; bad-debt socialization
//! lowers the supply index. Protocol revenue is held as scaled supply shares,
//! so it earns the supplier rate until claimed.
//!
//! ## Security notes
//!
//! - Every mutator requires the owner through `#[only_owner]`; views are public.
//! - Cash is an accounting book, separate from the token balance. A flash loan
//!   checks the token balance after payout, after the callback and after
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

**File:** contracts/controller/src/positions/supply.rs (L114-132)
```rust
    let pool_addr = cache.cached_pool_address();
    let mut entries: Vec<PoolSupplyEntry> = Vec::new(env);
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
    }

    let results = pool_supply_call(env, &pool_addr, &entries);
```

**File:** contracts/controller/src/positions/supply.rs (L140-157)
```rust
pub(crate) fn process_withdraw(
    env: &Env,
    caller: &Address,
    account_id: u64,
    withdrawals: &Vec<HubPayment>,
    to: Option<Address>,
) -> Vec<HubPayment> {
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_payments(env, withdrawals, payments::ZeroLeg::MeansAll);

    let paid = settle_withdraw(env, &mut account, &recipient, &aggregated, &mut cache);
```

**File:** contracts/pool/src/cache/cash.rs (L23-52)
```rust
    /// Increases accounting cash by `amount`. Rejects negative amounts and overflow.
    pub(crate) fn credit_cash(&mut self, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        self.cash = self
            .cash
            .checked_add(amount)
            .unwrap_or_else(|| panic_with_error!(&self.env, GenericError::MathOverflow));
    }

    /// Decreases accounting cash by `amount`. Rejects negative amounts or
    /// insufficient reserves.
    pub(crate) fn debit_cash(&mut self, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        self.require_reserves(amount);
        self.cash = self
            .cash
            .checked_sub(amount)
            .unwrap_or_else(|| panic_with_error!(&self.env, GenericError::MathOverflow));
    }

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

**File:** contracts/controller/src/markets.rs (L140-164)
```rust
/// Transfers funds to the pool, credits the measured receipt up to the backing
/// shortfall, and refunds unused funds. Returns credited cash; rejects flash loans.
pub(crate) fn recapitalize(
    env: &Env,
    payer: Address,
    hub_asset: HubAssetKey,
    amount: i128,
) -> i128 {
    validation::require_authorized_caller(env, &payer);
    require_positive_amount(env, amount);

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
}
```
