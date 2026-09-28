### Title
Tokens transferred directly to the pool are permanently untracked and unrecoverable — ([File: contracts/pool/src/cache/cash.rs](contracts/pool/src/cache/cash.rs))

### Summary
The `LiquidityPool` tracks liquidity in an internal `cash` ledger that is deliberately decoupled from the contract's real token balance. Every payout path (`withdraw`, `borrow`, `repay` refund, `recapitalize` refund, `claim_revenue`, `flash_loan`) debits tracked `cash` and transfers exactly the debited amount, and no entrypoint can release the untracked excess. Any token amount transferred directly to the pool address — which an unprivileged address can do with a plain `token.transfer` — is invisible to `cash`, backs no shares, and can never leave the contract.

### Finding Description
The pool's own documentation states the design: "Cash is an accounting book, separate from the token balance" [1](#0-0)  and "Tracked cash is a separate reserve balance that incidental token donations do not increase." [2](#0-1) 

All outbound transfers are driven by `Cache::transfer_out`, which only ever moves an amount that was first debited from tracked `cash` (`debit_cash` precedes `transfer_out` in `revenue::accounting`, `withdraw::apply`, `borrow::apply`). [3](#0-2) 

The complete mutator surface — `supply`, `borrow`, `withdraw`, `repay`, `recapitalize`, `flash_loan`, `create_strategy`, `seize_positions`, `net_settle`, `claim_revenue`, `update_indexes`, `update_params`, `upgrade` — contains no `sweep`/`recover`/`skim` equivalent; there is no path that computes `token.balance(pool) - cash` or moves untracked funds to anyone. [4](#0-3) 

This is the same bug class as the external report: value accrues to the contract outside the accounting that gates the only withdrawal path. In SuperVaultAggregator the fee balance is debited with no pull mechanism; here, real token balance accumulates outside `cash` while every pull mechanism is hard-capped by tracked `cash` (`burn_claimable_revenue` computes `min(cash, floor(revenue_value))`). [5](#0-4) 

The same applies to the controller: `claim_revenue_for_asset` measures the controller's balance delta and forwards only `received` to the accumulator; pre-existing or donated balances on the controller are never forwarded by any entrypoint. [6](#0-5) 

### Impact Explanation
Permanent freezing of funds. Tokens held by the pool above tracked `cash` are locked forever: no owner call, no claim, and no user operation can move them, because every transfer is bounded by internal debits and the contract has no recovery entrypoint. Unlike the swap-aggregator, which explicitly protects fee buckets but allows `sweep_balance` to recover the unreserved excess [7](#0-6) , the pool offers no equivalent. The locked amount also silently distorts any off-chain solvency check that reads `token.balance(pool)` instead of `get_reserves`.

### Likelihood Explanation
The trigger is an ordinary `token.transfer` to the pool (or controller) address — reachable by any unprivileged address and explicitly in scope. It does not require privilege, timing, or oracle manipulation; it happens whenever any user, integrator, or mistaken counterparty sends tokens to the contract directly rather than through `supply`/`repay`/`recapitalize`, or whenever a token-side mechanic (e.g. a rebasing/airdrop credit or a counterparty paying a debt owed to the protocol by direct transfer) increases the pool's balance without a matching `credit_cash` call.

### Recommendation
Add an owner-gated recovery entrypoint on the pool that transfers `token.balance(pool) - total_cash_owed` (tracked cash plus any reserved amounts) to a recipient, mirroring the swap-aggregator's `ReservedTotal`-protected `sweep_balance`. Alternatively, adopt measured-receipt crediting for all inbound flows and document a governance-run recovery procedure. On the controller, extend `claim_revenue_for_asset`-style measured forwarding or add a sweep so stray controller balances above tracked obligations are not permanently stuck.

### Proof of Concept
1. Market `(hub, USDC)` exists; `get_reserves` returns tracked `cash = C` and the pool's token balance is also `C`.
2. Any address calls `token.transfer(from: alice, to: pool, amount: X)` directly (not via `controller.supply`).
3. `get_reserves` still returns `C`; `token.balance(pool)` is `C + X`.
4. Enumerate every pool mutator: `withdraw`, `borrow`, `claim_revenue`, `flash_loan`, `net_settle` all cap outbound transfers at tracked `cash` debits; `supply`/`repay`/`recapitalize` only credit `cash` against controller-initiated transfers already measured; no entrypoint accepts a "recover excess" instruction.
5. `X` remains in the pool balance permanently — unclaimable by users (no shares minted), unclaimable as revenue (capped at `min(cash, revenue)`), and unsweepable by the owner (no such function).

### Citations

**File:** contracts/pool/src/lib.rs (L34-36)
```rust
//! - Cash is an accounting book, separate from the token balance. A flash loan
//!   checks the token balance after payout, after the callback and after
//!   repayment.
```

**File:** contracts/pool/src/lib.rs (L130-252)
```rust
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
    }
```

**File:** docs/reference/formulas.md (L80-82)
```markdown
Reclassifying seized collateral as revenue leaves total supply unchanged.
Tracked cash is a separate reserve balance that incidental token donations do
not increase.
```

**File:** contracts/pool/src/ops/revenue.rs (L42-48)
```rust
    let net_transfer = cache.burn_claimable_revenue();

    guards::require_utilization_below_max(env, &cache);
    guards::require_supply_for_debt(env, &cache);
    cache.debit_cash(net_transfer);

    cache.commit();
```

**File:** contracts/pool/src/cache/shares.rs (L54-58)
```rust
    pub(crate) fn burn_claimable_revenue(&mut self) -> i128 {
        let treasury_actual = self.unscale_supply_floor(self.revenue);
        let amount = self.cash.min(treasury_actual);
        if amount <= 0 {
            return 0;
```

**File:** contracts/controller/src/markets.rs (L180-197)
```rust
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

**File:** contracts/swap-aggregator/src/lib.rs (L189-202)
```rust
    fn sweep_balance(env: Env, recipient: Address, tokens: Vec<Address>) {
        renew_instance(&env);
        let router = env.current_contract_address();
        let n = tokens.len();
        for i in 0..n {
            // `i < n == tokens.len()`, so the index is in range by construction.
            let token = tokens.get_unchecked(i);
            let client = token::Client::new(&env, &token);
            let balance = client.balance(&router);
            let reserved = storage::reserved_fee_balance(&env, &token);
            if balance > reserved {
                client.transfer(&router, &recipient, &(balance - reserved));
            }
        }
```
