### Title
Tokens sent directly to the liquidity pool cannot be rescued - (File: contracts/pool/src/lib.rs)

### Summary
The pool can receive listed tokens, including native XLM through its Stellar Asset Contract, by direct `token.transfer`. Such transfers increase the pool’s physical token balance but do not credit any market’s `cash`, supply, debt, or revenue accounting. No pool or controller entrypoint can withdraw this unbooked surplus.

### Finding Description
Market withdrawals only debit booked `cash`, so an unsolicited transfer is not included in withdrawable reserves. [1](#0-0) 

`claim_revenue` is also bounded by claimable revenue shares and debits the same cash book, so it cannot extract a donation that was never booked as revenue. [2](#0-1) 

`recapitalize` credits only up to a market’s backing shortfall and refunds the rest of that call’s inbound amount; it does not sweep an already-existing surplus. [3](#0-2) 

The codebase explicitly models a direct donation as belonging to no market’s cash book while remaining in the shared physical pool balance. [4](#0-3) 

The pool interface exposes market mutations, withdrawals, revenue claims, recapitalization, and flash operations, but no generic token sweep or rescue function. [5](#0-4) 

### Impact Explanation
An unprivileged user who directly transfers a listed asset or native XLM to the pool loses those funds under the deployed ABI. The tokens remain in the contract’s balance, cannot be attributed to a position, and cannot be withdrawn through any existing user-facing or administrative market operation. Recovery would require a privileged code upgrade rather than an existing rescue path.

### Likelihood Explanation
The trigger is an accidental direct SAC transfer to the pool address. This is plausible because users can transfer tokens to arbitrary contract addresses, while the pool silently accepts the balance without crediting or rejecting it. The probability depends on user error, but any amount sent this way becomes stranded.

### Recommendation
Add an owner/governance-controlled `sweep_surplus` path for pool-held tokens. For each listed asset, calculate the physical balance minus the aggregate obligations shared by all hub markets using that token and allow only the excess to be swept. This avoids disturbing supplier, borrower, or protocol-revenue backing. A generic arbitrary-token rescue can also be added for unlisted assets.

### Proof of Concept
1. Let `pool` be the deployed `LiquidityPool`, `asset` a listed token or native XLM SAC, and `alice` any unprivileged account.
2. Record `reserves_before = pool.get_reserves(HubAssetKey { hub_id, asset })`.
3. Invoke `token::Client(asset).transfer(alice, pool, amount)` directly.
4. The pool’s token balance increases by `amount`, while `pool.get_reserves(HubAssetKey { hub_id, asset })` remains `reserves_before` because no supply, debt, cash, or revenue shares were credited.
5. Alice cannot recover the transfer through `Controller::withdraw` because she owns no corresponding supply position, and pool withdrawals are limited by booked cash.
6. `Controller::claim_revenue` cannot recover it because the donation did not create revenue shares.
7. `Controller::recapitalize` cannot recover it because excess from a new recapitalization call is refunded to its payer, while the previously transferred surplus remains unbooked.
8. The exposed pool interface contains no sweep or arbitrary transfer endpoint, leaving the `amount` stranded under the current contract code.

### Citations

**File:** contracts/pool/src/ops/withdraw.rs (L111-119)
```rust
fn gate_and_debit(env: &Env, cache: &mut Cache, net_transfer: i128, skip_utilization_check: bool) {
    cache.require_reserves(net_transfer);

    if !skip_utilization_check {
        guards::require_utilization_below_max(env, cache);
    }
    guards::require_supply_for_debt(env, cache);
    cache.debit_cash(net_transfer);
}
```

**File:** contracts/pool/src/ops/revenue.rs (L42-46)
```rust
    let net_transfer = cache.burn_claimable_revenue();

    guards::require_utilization_below_max(env, &cache);
    guards::require_supply_for_debt(env, &cache);
    cache.debit_cash(net_transfer);
```

**File:** contracts/pool/src/ops/recapitalize.rs (L52-58)
```rust
    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();
```

**File:** tests/test-harness/tests/pool_money_flow_audit.rs (L86-96)
```rust
    // An unsolicited donation belongs to no market's cash book.
    market.token_admin.mint(&payer, &(7 * UNIT));
    token.transfer(&payer, &market.pool, &(7 * UNIT));
    let check = |supply, debt, label: &str| {
        let state = books(&t, &key, supply, debt);
        let other = books(&t, &second, secondary_supply, 0);
        assert_eq!(other.cash, 100 * UNIT);
        assert_eq!(
            token.balance(&market.pool),
            state.cash + other.cash + 7 * UNIT
        );
```

**File:** contracts/pool/src/lib.rs (L128-251)
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

    /// Credits cash up to the market's backing shortfall
    /// (`guards::backing_shortfall`) and transfers the excess back to `payer`.
    /// The controller transfers `amount` in before this call. Restricted to
    /// the owner; returns a [`PoolAmountMutation`] with the amount applied.
    #[only_owner]
    fn recapitalize(
        env: Env,
        hub_asset: HubAssetKey,
        payer: Address,
        amount: i128,
    ) -> PoolAmountMutation {
        ops::recapitalize::apply(&env, hub_asset, payer, amount)
    }

    /// Transfers out, invokes `execute_flash_loan` on the receiver, pulls
    /// principal plus fee back via `transfer_from`, and books the fee as
    /// protocol revenue. Returns the fee. Owner-only; requires the market to
    /// allow flash loans.
    #[only_owner]
    fn flash_loan(
        env: Env,
        hub_asset: HubAssetKey,
        initiator: Address,
        receiver: Address,
        amount: i128,
        data: Bytes,
    ) -> i128 {
        ops::flash::apply(&env, hub_asset, initiator, receiver, amount, data)
    }

    /// Mints debt for `action.amount`, books the fee as protocol revenue when
    /// `charge_fee`, and sends `amount - fee` to `receiver`. Owner-only.
    #[only_owner]
    fn create_strategy(
        env: Env,
        receiver: Address,
        action: PoolAction,
        charge_fee: bool,
    ) -> PoolStrategyMutation {
        ops::strategy::apply(&env, &receiver, action, charge_fee)
    }

    /// Seizes positions during liquidation or bad-debt cleanup. Borrow-side
    /// entries socialize bad debt onto the supply index and burn the debt;
    /// deposit-side entries reclassify supply shares as protocol revenue.
    /// Restricted to the owner.
    #[only_owner]
    fn seize_positions(env: Env, entries: Vec<PoolSeizeEntry>) {
        ops::run_batch(&env, entries, |e, entry| ((), ops::seize::apply(e, entry)));
    }

    /// Nets supply against debt on one market with no cash movement, capped by
    /// the conservative overlap of floored supply and ceiled debt. Owner-only.
    #[only_owner]
    fn net_settle(env: Env, entry: PoolNetSettleEntry) -> PoolNetSettleResult {
        renew_instance(&env);
        let (result, snapshot) = ops::net_settle::apply(&env, &entry);
        events::emit_market_state(&env, snapshot);
        result
    }

    /// Burns claimable revenue shares, debits cash and pays the owner the lesser
    /// of cash and revenue's floored token value. Returns zero when nothing is
    /// claimable. Owner-only.
    ///
    /// Decrements the snapshot `revenue` field, so that field is not a
    /// cumulative counter.
    #[only_owner]
    fn claim_revenue(env: Env, hub_asset: HubAssetKey) -> PoolAmountMutation {
        ops::revenue::apply(&env, hub_asset)
```
