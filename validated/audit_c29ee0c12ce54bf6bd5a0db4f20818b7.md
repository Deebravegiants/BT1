### Title
Flash-position callback can resurrect a deleted account and strand pool debt - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
`flash_position` keeps an `Account` loaded before the external receiver callback and persists that stale object afterward without revalidating that the account still exists. A receiver can execute a ready governance `ForceSocializeBadDebt` operation for the same account during the callback, causing the account metadata and NFT to be deleted before the outer call writes the stale position maps back. [1](#0-0) [2](#0-1) 

### Finding Description
The controller authenticates the caller, loads the account, and then mints fee-free debt before invoking the attacker-selected Wasm receiver. [3](#0-2)  Governance permits anyone to execute a ready operation with `executor = None`, and `AdminOperation::ForceSocializeBadDebt(account_id)` resolves to the controller's `force_socialize_bad_debt` method. [4](#0-3) [5](#0-4) 

The receiver can therefore invoke `Governance::execute(None, controller, "force_socialize_bad_debt", [account_id], predecessor, salt)` inside `execute_flash_position`. [6](#0-5)  Bad-debt cleanup removes the account entry and burns its NFT. [7](#0-6) [8](#0-7) 

After the callback, `process_flash_position` still uses the pre-callback `account`, deposits measured collateral, checks the stale in-memory maps, and calls `strategy_finalize`. [9](#0-8)  `persist_account_positions` writes the stale supply and debt maps under `account_id`, while `renew_user_account` only renews keys that exist and does not recreate deleted metadata. [2](#0-1) [10](#0-9) 

### Impact Explanation
The receiver retains the flashed debt tokens because `mint_and_forward` transfers the measured pool proceeds to it. [11](#0-10)  The final write leaves orphaned supply and debt positions for an account whose metadata and ownership NFT no longer exist. [12](#0-11) [13](#0-12) 

Every later operation that loads the account through `get_account` fails because missing metadata or unresolved NFT ownership returns `AccountNotFound`. [14](#0-13)  Consequently, the orphaned debt cannot be repaid, liquidated, withdrawn against, or cleaned through the normal controller paths, while the collateral remains locked and the debt-asset liquidity has already left the pool. [15](#0-14) 

This causes permanent freezing of the deposited collateral and a permanent unrecoverable debt position, potentially leaving the corresponding pool market insolvent. [16](#0-15) [14](#0-13) 

### Likelihood Explanation
Likelihood is Medium: the attacker needs an existing Multiply-compatible account and a ready governance cleanup operation for that account, but executing that ready operation does not require a privileged executor when `executor` is `None`. [4](#0-3) [17](#0-16) 

The attack path is otherwise fully reachable by one unprivileged caller controlling both the account and the flash receiver. [18](#0-17) 

### Recommendation
Reload the account metadata and NFT owner after `invoke_receiver`, and abort if the account no longer exists. [19](#0-18) [20](#0-19) 

Additionally, make owner-only lifecycle operations that can delete accounts—especially `force_socialize_bad_debt`—reject while `is_flash_loan_ongoing` is true, or record an account existence/generation epoch before the callback and verify it before persistence. [21](#0-20) [22](#0-21) 

### Proof of Concept
1. Create or use an attacker-owned account `A` in `PositionMode::Multiply`, with enough existing state for the scheduled `ForceSocializeBadDebt(A)` operation to execute successfully. [23](#0-22) [5](#0-4) 
2. Wait until the governance operation is ready. [24](#0-23) 
3. Call:

```rust
Controller::flash_position(
    caller,
    A,
    spoke_id,
    PositionMode::Multiply,
    debt_asset,
    borrow_amount,
    attacker_receiver,
    callback_data,
    vec![(collateral_asset, minimum_collateral)],
    vec![],
)
```

4. The controller loads `A`, mints `borrow_amount` of debt through the pool, and transfers the measured proceeds to `attacker_receiver`. [3](#0-2) [11](#0-10) 
5. In `execute_flash_position`, `attacker_receiver` calls:

```rust
Governance::execute(
    None,
    controller,
    "force_socialize_bad_debt",
    vec![A.into_val(&env)],
    predecessor,
    salt,
)
```

6. The ready operation deletes `A`'s metadata and position maps and burns its position NFT. [13](#0-12) [8](#0-7) 
7. The receiver transfers enough collateral tokens to the controller so the post-callback balance deltas satisfy `collaterals`. [25](#0-24) 
8. The outer call continues with the deleted account's stale in-memory copy, writes supply and debt maps for `A`, and finishes without restoring metadata or the NFT. [9](#0-8) [26](#0-25) 
9. Future calls that use `get_account(A)` fail because metadata and NFT ownership are missing, leaving the newly created debt unreachable while the attacker retains the borrowed tokens. [14](#0-13)

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L40-84)
```rust
pub(crate) fn process_flash_position(
    env: &Env,
    caller: &Address,
    params: FlashPositionParams<'_>,
) -> u64 {
    require_authorized_caller(env, caller);

    let FlashPositionParams {
        account_id,
        spoke_id,
        mode,
        debt,
        amount,
        receiver,
        data,
        collaterals,
        refund_assets,
    } = params;

    require_positive_amount(env, amount);
    config::require_hub_active(env, debt.hub_id);
    assert_with_error!(
        env,
        matches!(
            mode,
            PositionMode::Multiply | PositionMode::Long | PositionMode::Short
        ),
        CollateralError::InvalidPositionMode
    );
    require_wasm_receiver(env, receiver);

    let controller = env.current_contract_address();
    assert_with_error!(
        env,
        *receiver != controller,
        FlashLoanError::InvalidFlashloanReceiver
    );

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    assert_with_error!(
        env,
        *receiver != pool_addr,
        FlashLoanError::InvalidFlashloanReceiver
    );
```

**File:** contracts/controller/src/strategies/flash_position.rs (L93-154)
```rust
    let (account_id, mut account) = account::load_or_create_account(
        env,
        caller,
        account_id,
        spoke_id,
        mode,
        account::AccountGuard::Multiply,
        &mut cache,
    );

    validate_collaterals(env, &mut cache, &account, collaterals);
    validate_refund_assets(
        env,
        &mut cache,
        account.spoke_id,
        debt.hub_id,
        collaterals,
        refund_assets,
    );

    let mut extra_assets = vec![env, debt.asset.clone()];
    for (hub_asset, _) in collaterals.iter() {
        extra_assets.push_back(hub_asset.asset.clone());
    }
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

    // Guard both forwarding and the callback: token hooks can reenter first.
    let (amount_received, collateral_before, refund_before) =
        storage::with_flash_guard(env, || {
            let amount_received =
                mint_and_forward(env, &mut account, debt, amount, receiver, &mut cache);
            // Baselines exclude funding and forwarding; count callback receipts only.
            let collateral_before = snapshot_balances(
                env,
                &controller,
                collaterals.iter().map(|(hub_asset, _)| hub_asset.asset),
            );
            let refund_before = snapshot_balances(env, &controller, refund_assets.iter());
            invoke_receiver(
                env,
                receiver,
                caller,
                account_id,
                &debt.asset,
                amount,
                amount_received,
                &controller,
                data,
            );
            (amount_received, collateral_before, refund_before)
        });

    let deposits = collect_collateral_deposits(env, &controller, collaterals, &collateral_before);
    process_deposit(env, &controller, &mut account, &deposits, &mut cache);

    refund_listed_assets(env, caller, refund_assets, &refund_before);

    // Check before and after finalization: its LTV refresh can prune zero-scaled
    // supply, and persistence removes empty accounts.
    require_flash_position_still_open(env, &account, debt);
    strategy_finalize(env, account_id, &mut account, &mut cache);
    require_flash_position_still_open(env, &account, debt);
```

**File:** contracts/controller/src/strategies/flash_position.rs (L258-295)
```rust
/// Mints fee-free debt, verifies the controller receipt against the pool result,
/// then forwards it and returns the receiver's measured receipt.
fn mint_and_forward(
    env: &Env,
    account: &mut Account,
    debt: &HubAssetKey,
    amount: i128,
    receiver: &Address,
    cache: &mut Context,
) -> i128 {
    let controller = env.current_contract_address();
    let before = token::Client::new(env, &debt.asset).balance(&controller);

    let reported = borrow_into_controller(
        env,
        account,
        debt,
        amount,
        false,
        PositionAction::FlashPos,
        cache,
    );

    let measured = balance_delta_since(env, &debt.asset, &controller, before);
    assert_with_error!(env, measured == reported, GenericError::InternalError);
    assert_with_error!(env, measured > 0, GenericError::AmountMustBePositive);

    let forwarded = transfer_amount_measured(
        env,
        &debt.asset,
        &controller,
        receiver,
        measured,
        GenericError::AmountMustBePositive,
    );
    assert_with_error!(env, forwarded > 0, GenericError::AmountMustBePositive);
    forwarded
}
```

**File:** contracts/controller/src/positions/mod.rs (L153-184)
```rust
pub(crate) fn persist_account_positions(
    env: &Env,
    account_id: u64,
    account: &Account,
    sides: PositionSides,
    remove_if_empty: bool,
) {
    if sides != PositionSides::Debt {
        storage::set_supply_positions(env, account_id, &account.supply_positions);
    }
    if sides != PositionSides::Supply {
        storage::set_debt_positions(env, account_id, &account.borrow_positions);
    }
    storage::renew_user_account(env, account_id);
    if remove_if_empty {
        account::cleanup_account_if_empty(env, account, account_id);
    }
}

/// Persists spoke usage and positions, then emits the position-update batch.
pub(crate) fn finalize_position_flow(
    env: &Env,
    account_id: u64,
    account: &Account,
    cache: &mut Context,
    sides: PositionSides,
    remove_if_empty: bool,
) {
    cache.persist_spoke_usage();
    persist_account_positions(env, account_id, account, sides, remove_if_empty);
    cache.emit_position_batch(account_id, account);
}
```

**File:** contracts/governance/src/api.rs (L53-67)
```rust
    /// Executes a ready, non-expired scheduled op against `target` (not this
    /// contract). If `executor` is `Some`, requires that address to auth and
    /// hold `EXECUTOR_ROLE`; if `None`, no executor role check (anyone may
    /// drive execution of a ready op). Clears scheduled state on success.
    fn execute(
        env: Env,
        executor: Option<Address>,
        target: Address,
        function: Symbol,
        args: Vec<Val>,
        predecessor: BytesN<32>,
        salt: BytesN<32>,
    ) -> Val {
        lifecycle::execute(&env, executor, target, function, args, predecessor, salt)
    }
```

**File:** contracts/governance/src/op.rs (L407-410)
```rust
        AdminOperation::ForceSocializeBadDebt(account_id) => sensitive_controller_operation(
            env,
            "force_socialize_bad_debt",
            vec![env, account_id.into_val(env)],
```

**File:** contracts/governance/src/timelock/lifecycle.rs (L81-109)
```rust
/// Executes a scheduled operation against `target` once its delay has elapsed and
/// it has not expired, and returns the invocation's result. Rejects operations
/// that target this contract itself (use `execute_self` for those). Clears the
/// operation's scheduled state on completion.
pub(crate) fn execute(
    env: &Env,
    executor: Option<Address>,
    target: Address,
    function: Symbol,
    args: Vec<Val>,
    predecessor: BytesN<32>,
    salt: BytesN<32>,
) -> Val {
    assert_with_error!(
        env,
        target != env.current_contract_address(),
        GenericError::InternalError
    );
    let operation = Operation {
        target,
        function,
        args,
        predecessor,
        salt,
    };
    let operation_id = prepare_execute(env, executor.as_ref(), &operation);
    let result = execute_operation(env, &operation);
    finish_execute(env, &operation_id);
    result
```

**File:** contracts/controller/src/positions/liquidation/bad_debt.rs (L14-60)
```rust
pub(crate) fn execute_bad_debt_cleanup(
    env: &Env,
    cache: &mut Context,
    account_id: u64,
    account: &Account,
    totals: &AccountRiskTotals,
) {
    let mut entries: Vec<PoolSeizeEntry> = Vec::new(env);
    for (hub_asset, position) in iter_typed_positions(&account.supply_positions) {
        cache.apply_spoke_exit(
            account.spoke_id,
            UsageSide::Supply,
            &hub_asset,
            position.scaled_amount,
        );
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Deposit,
            position: (&position).into(),
        });
    }
    for (hub_asset, position) in iter_debt_positions(&account.borrow_positions) {
        cache.apply_spoke_exit(
            account.spoke_id,
            UsageSide::Borrow,
            &hub_asset,
            position.scaled_amount,
        );
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Borrow,
            position: (&position).into(),
        });
    }
    let pool_addr = cache.cached_pool_address();
    pool_seize_positions_call(env, &pool_addr, &entries);

    cache.persist_spoke_usage();

    CleanBadDebtEvent {
        account_id,
        total_borrow_usd_wad: totals.total_debt.raw(),
        total_collateral_usd_wad: totals.total_collateral.raw(),
    }
    .publish(env);

    remove_account_and_burn_nft(env, account_id);
```

**File:** contracts/controller/src/account.rs (L86-111)
```rust
pub(crate) fn load_or_create_account(
    env: &Env,
    caller: &Address,
    account_id: u64,
    spoke_id: u32,
    mode: PositionMode,
    guard: AccountGuard,
    cache: &mut Context,
) -> (u64, Account) {
    if account_id == 0 {
        return create_account(env, caller, spoke_id, mode, cache);
    }
    let account = storage::get_account(env, account_id);
    match guard {
        AccountGuard::Supply => require_spoke_match(env, &account, spoke_id),
        AccountGuard::Migrate => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
        }
        AccountGuard::Multiply => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
            assert_with_error!(env, account.mode == mode, GenericError::AccountModeMismatch);
        }
    }
    (account_id, account)
```

**File:** contracts/controller/src/account.rs (L157-169)
```rust
/// Deletes all account entries and burns its NFT atomically. Account deletion
/// must use this path to preserve the NFT/account existence invariant.
pub(crate) fn remove_account_and_burn_nft(env: &Env, account_id: u64) {
    storage::remove_account_entry(env, account_id);
    let nft = storage::get_position_nft(env);
    nft_burn_call(env, &nft, account_id);
}

/// Deletes the account and burns its NFT when both position maps are empty.
pub(crate) fn cleanup_account_if_empty(env: &Env, account: &Account, account_id: u64) {
    if account.is_empty() {
        remove_account_and_burn_nft(env, account_id);
    }
```

**File:** contracts/controller/src/storage/account.rs (L75-105)
```rust
/// Stores supply positions without renewing TTL; deletes an empty map.
pub(crate) fn set_supply_positions(
    env: &Env,
    account_id: u64,
    map: &Map<HubAssetKey, AccountPositionRaw>,
) {
    write_side_map(env, &ControllerKey::SupplyPositions(account_id), map);
}

/// Stores debt positions without renewing TTL; deletes an empty map.
pub(crate) fn set_debt_positions(
    env: &Env,
    account_id: u64,
    map: &Map<HubAssetKey, DebtPositionRaw>,
) {
    write_side_map(env, &ControllerKey::BorrowPositions(account_id), map);
}

/// Stores a nonempty position map without renewing TTL; deletes an empty map.
fn write_side_map<V: TryFromVal<Env, Val> + IntoVal<Env, Val>>(
    env: &Env,
    key: &ControllerKey,
    map: &Map<HubAssetKey, V>,
) {
    let persistent = env.storage().persistent();
    if map.is_empty() {
        persistent.remove(key);
    } else {
        persistent.set(key, map);
    }
}
```

**File:** contracts/controller/src/storage/account.rs (L144-161)
```rust
/// Loads both position maps and current NFT ownership. Missing metadata or
/// unresolved ownership fails with `AccountNotFound`.
pub(crate) fn get_account(env: &Env, account_id: u64) -> Account {
    try_get_account(env, account_id)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::AccountNotFound))
}

/// Loads both position maps and current NFT ownership; returns `None` when
/// metadata is absent or ownership cannot be resolved.
pub(crate) fn try_get_account(env: &Env, account_id: u64) -> Option<Account> {
    let meta = try_get_account_meta(env, account_id)?;
    let owner = try_account_owner(env, account_id)?;
    Some(account_from_parts(
        owner,
        meta,
        get_supply_positions(env, account_id),
        get_debt_positions(env, account_id),
    ))
```

**File:** contracts/controller/src/storage/account.rs (L249-270)
```rust
/// Deletes metadata, both position maps, and delegates. Does not burn the NFT.
pub(crate) fn remove_account_entry(env: &Env, account_id: u64) {
    let persistent = env.storage().persistent();
    persistent.remove(&ControllerKey::AccountMeta(account_id));
    persistent.remove(&ControllerKey::SupplyPositions(account_id));
    persistent.remove(&ControllerKey::BorrowPositions(account_id));
    persistent.remove(&ControllerKey::Delegates(account_id));
}

/// Renews user TTL for each existing account entry; does not renew the NFT.
pub(crate) fn renew_user_account(env: &Env, account_id: u64) {
    let persistent = env.storage().persistent();
    let keys = [
        ControllerKey::AccountMeta(account_id),
        ControllerKey::SupplyPositions(account_id),
        ControllerKey::BorrowPositions(account_id),
        ControllerKey::Delegates(account_id),
    ];
    for key in &keys {
        if persistent.has(key) {
            renew_user_key(env, key);
        }
```

**File:** contracts/controller/src/storage/account.rs (L284-313)
```rust
/// Returns the temporary flash-loan flag, defaulting to false.
pub(crate) fn is_flash_loan_ongoing(env: &Env) -> bool {
    env.storage()
        .temporary()
        .get(&SessionKey::FlashLoanOngoing)
        .unwrap_or(false)
}

/// Sets the temporary flash-loan flag, or removes it when clearing.
pub(crate) fn set_flash_loan_ongoing(env: &Env, ongoing: bool) {
    if ongoing {
        env.storage()
            .temporary()
            .set(&SessionKey::FlashLoanOngoing, &true);
    } else {
        env.storage()
            .temporary()
            .remove(&SessionKey::FlashLoanOngoing);
    }
}

/// Runs `f` with the flash-loan flag set; preserves an already-active outer guard.
pub(crate) fn with_flash_guard<T>(env: &Env, f: impl FnOnce() -> T) -> T {
    let prev = is_flash_loan_ongoing(env);
    set_flash_loan_ongoing(env, true);
    let out = f();
    if !prev {
        set_flash_loan_ongoing(env, false);
    }
    out
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L42-49)
```rust
) -> u64 {
    liquidator.require_auth();
    validation::require_not_flash_loaning(env);

    let mut account = storage::get_account(env, account_id);

    let mut cache = Context::new(env);

```
