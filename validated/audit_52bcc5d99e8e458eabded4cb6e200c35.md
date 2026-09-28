### Title
`Controller::withdraw` can permanently strand collateral at an arbitrary contract recipient - (File: contracts/controller/src/positions/supply.rs)

### Summary
Medium. `withdraw` accepts a user-supplied `to` address and only rejects the pool and controller addresses, so an account owner or delegate can send withdrawn collateral to a contract that cannot move or recover tokens. [1](#0-0) [2](#0-1) 

### Finding Description
`Controller::withdraw(caller, account_id, withdrawals, to)` resolves `to` to the caller only when it is `None`; otherwise it uses the supplied address. [3](#0-2)  The sole recipient sanity check is `require_external_recipient`, which rejects only `env.current_contract_address()` and the configured pool address. [2](#0-1)  The controller then forwards that recipient to `pool.withdraw`, and the pool transfers the net withdrawal directly to it with `token.transfer`. [4](#0-3) [5](#0-4) 

`Controller::borrow` has the same recipient flow: it accepts `to`, rejects only the controller and pool, and the pool transfers the borrowed assets to that receiver. [6](#0-5) [7](#0-6) 

### Impact Explanation
A withdrawal burns or reduces the user's supply position and sends the underlying asset to the selected contract address. [8](#0-7) [9](#0-8)  If that contract has no token-transfer or recovery path, the funds remain locked at the contract address while the user's position has already been reduced. [10](#0-9)  With `borrow`, the same mistake additionally leaves the account with debt while the borrowed assets are stuck at the contract. [11](#0-10) 

### Likelihood Explanation
The path is directly reachable by an account owner or delegate through the public `withdraw` or `borrow` entrypoints. [12](#0-11)  Third-party recipients are intentionally supported, as shown by the withdraw-to-recipient test, and the regression tests only require the pool and controller recipients to fail. [13](#0-12) [14](#0-13)  The likelihood is limited by the need for the authorized caller to supply an unsuitable contract address, but no protocol check prevents that input.

### Recommendation
Do not silently accept arbitrary contract recipients for user-facing `withdraw` and `borrow` payouts. At minimum, reject known protocol infrastructure and add an explicit integration-facing path or confirmation mechanism for contract recipients; if arbitrary contract payouts are not required, reject `Address` values that are contracts. The existing `require_external_recipient` check is the central place to enforce this policy. [15](#0-14) 

### Proof of Concept
1. Alice owns a lending account with a withdrawable USDC position.
2. Alice calls:

```rust
ControllerClient::new(&env, &controller).withdraw(
    &alice,
    &account_id,
    &vec![&env, (usdc_hub_asset, amount)],
    &Some(sink_contract),
);
```

3. `process_withdraw` accepts `sink_contract` because it is neither the controller nor the pool. [16](#0-15) [2](#0-1) 
4. The pool burns Alice's supply shares and transfers the USDC to `sink_contract`. [17](#0-16) [9](#0-8) 
5. If `sink_contract` exposes no method that can transfer or recover the token, the withdrawal is permanently frozen at that address. [5](#0-4)

### Citations

**File:** contracts/controller/src/lib.rs (L104-128)
```rust
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
    }

    /// Withdraws collateral to `to` or the caller and returns actual amounts in
    /// asset units. Zero withdraws an asset's full position. Requires owner or
    /// delegate authorization and post-withdrawal solvency.
    fn withdraw(
        env: Env,
        caller: Address,
        account_id: u64,
        withdrawals: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) -> Vec<(HubAssetKey, i128)> {
        positions::process_withdraw(&env, &caller, account_id, &withdrawals, to)
    }
```

**File:** contracts/controller/src/positions/mod.rs (L33-42)
```rust
/// Rejects pool and controller recipients with `InvalidFlashloanReceiver`.
/// Pool self-transfers debit cash without moving tokens; controller receipts
/// would remain unclaimed by balance-delta accounting.
pub(crate) fn require_external_recipient(env: &Env, cache: &mut Context, recipient: &Address) {
    let pool = cache.cached_pool_address();
    assert_with_error!(
        env,
        *recipient != env.current_contract_address() && *recipient != pool,
        FlashLoanError::InvalidFlashloanReceiver
    );
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

**File:** contracts/controller/src/positions/supply.rs (L181-214)
```rust
    for (hub_asset, amount) in aggregated.iter() {
        enforce_spoke_asset_flags(
            env,
            cache,
            account.spoke_id,
            &hub_asset,
            FreezePolicy::AllowOnExit,
        );
        let position = get_supply_position_or_panic(env, account, &hub_asset);
        let requested = if amount == 0 {
            WITHDRAW_ALL_SENTINEL
        } else {
            amount
        };
        entries.push_back(PoolWithdrawEntry {
            action: make_pool_action(&position, requested, hub_asset.clone()),
            protocol_fee: 0,
        });
    }

    let results = apply_withdraw_batch(
        env,
        account,
        recipient,
        WithdrawKind::Normal,
        events::PositionAction::Withdraw,
        &entries,
        cache,
    );
    let mut paid: Vec<HubPayment> = Vec::new(env);
    for_each_leg(env, &entries, &results, |entry, result| {
        paid.push_back((entry.action.hub_asset, result.actual_amount));
    });
    paid
```

**File:** contracts/controller/src/external/pool.rs (L54-61)
```rust
pub(crate) fn pool_withdraw_call(
    env: &Env,
    pool_addr: &Address,
    receiver: &Address,
    is_liquidation: bool,
    entries: &Vec<PoolWithdrawEntry>,
) -> Vec<PoolPositionMutation> {
    LiquidityPoolClient::new(env, pool_addr).withdraw(receiver, &is_liquidation, entries)
```

**File:** contracts/pool/src/cache/cash.rs (L46-52)
```rust
    pub(crate) fn transfer_out(&self, recipient: &Address, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        if amount == 0 {
            return;
        }
        let tok = token::Client::new(&self.env, &self.params.asset_id);
        tok.transfer(&self.env.current_contract_address(), recipient, &amount);
```

**File:** contracts/controller/src/positions/debt.rs (L33-57)
```rust
pub(crate) fn process_borrow(
    env: &Env,
    caller: &Address,
    account_id: u64,
    borrows: &Vec<HubPayment>,
    to: Option<Address>,
) {
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_positive_payments(env, borrows);

    validate_position_entry_gates(
        env,
        &account,
        &aggregated,
        &mut cache,
        AccountPositionType::Borrow,
    );
    settle_borrow(env, &mut account, &recipient, &aggregated, &mut cache);
```

**File:** contracts/pool/src/ops/borrow.rs (L25-35)
```rust
pub(crate) fn apply(
    env: &Env,
    receiver: &Address,
    entry: &PoolBorrowEntry,
) -> (PoolPositionMutation, MarketStateSnapshot) {
    let outcome = accounting(env, entry);

    outcome
        .cache
        .transfer_out(receiver, outcome.mutation.actual_amount);
    (outcome.mutation, outcome.snapshot)
```

**File:** contracts/pool/src/ops/borrow.rs (L42-50)
```rust
pub(crate) fn accounting(env: &Env, entry: &PoolBorrowEntry) -> BorrowOutcome {
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    mint_debt(env, &mut cache, &mut position, amount);
    cache.debit_cash(amount);

    let snapshot = cache.commit();
    let mutation = cache.position_mutation(position, amount);
```

**File:** contracts/pool/src/ops/withdraw.rs (L38-49)
```rust
    if outcome.net_transfer == 0
        && (entry.action.position.scaled_amount > 0 || entry.action.amount == i128::MAX)
        && outcome.mutation.position.scaled_amount == 0
    {
        let _ = token::Client::new(env, &outcome.cache.params().asset_id).try_transfer(
            &env.current_contract_address(),
            receiver,
            &0,
        );
    } else {
        outcome.cache.transfer_out(receiver, outcome.net_transfer);
    }
```

**File:** tests/test-harness/tests/controller/withdraw.rs (L247-268)
```rust
fn test_withdraw_to_pays_third_party_recipient() {
    let mut t = LendingTest::new()
        .with_market(usdc_preset())
        .with_dust_disabled_all_markets()
        .build();

    t.supply(ALICE, "USDC", 10_000.0);
    let bob = t.get_or_create_user(test_harness::BOB);

    let alice_wallet_before = t.token_balance_raw(ALICE, "USDC");
    let bob_wallet_before = t.token_balance_raw(test_harness::BOB, "USDC");

    let paid = t.withdraw_to_raw(ALICE, "USDC", 30_000_000_000, &bob);
    let (_, paid_amount) = paid.get(0).unwrap();
    assert_eq!(paid_amount, 30_000_000_000);

    assert_eq!(
        t.token_balance_raw(test_harness::BOB, "USDC") - bob_wallet_before,
        30_000_000_000
    );
    assert_eq!(t.token_balance_raw(ALICE, "USDC"), alice_wallet_before);
    t.assert_supply_near(ALICE, "USDC", 7_000.0, 1.0);
```

**File:** tests/test-harness/tests/controller/recipient_is_protocol_contract.rs (L48-60)
```rust
fn withdraw_to_the_pool_or_the_controller_is_rejected() {
    let mut t = setup();
    let id = t.account_id(ALICE);
    let alice = t.get_or_create_user(ALICE);
    let leg = vec![&t.env, (hub_asset(t.resolve_asset("USDC")), U)];
    for bad in [t.get_pool_address("USDC"), t.controller_address()] {
        let flat: Result<(), soroban_sdk::Error> =
            match t.ctrl_client().try_withdraw(&alice, &id, &leg, &Some(bad)) {
                Ok(_) => Ok(()),
                Err(e) => Err(e.expect("expected a contract error, got an InvokeError")),
            };
        assert_contract_error(flat, errors::INVALID_FLASHLOAN_RECEIVER);
    }
```

**File:** contracts/pool/src/lib.rs (L150-162)
```rust
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
```
