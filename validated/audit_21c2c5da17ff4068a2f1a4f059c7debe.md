### Title
Stale spoke-asset configuration survives a mid-transaction governance update in `flash_position` - ([File: contracts/controller/src/strategies/flash_position.rs])

### Summary

`flash_position` creates one invocation-local `Context` before invoking the attacker-controlled flash receiver. That context caches spoke-asset admission and risk parameters. The receiver can execute an already-ready governance operation during the callback, changing or removing the spoke-asset configuration, after which the controller continues using the pre-callback cached configuration for collateral deposit accounting and final solvency checks.

### Finding Description

`process_flash_position` initializes `Context` before the callback and uses it for pool data, spoke-asset checks, market indexes, and risk evaluation [1](#0-0) .

The callback boundary is `invoke_receiver`, which calls `execute_flash_position` on a caller-selected Wasm contract [2](#0-1) .

Before the callback, `validate_collaterals` calls `require_can_supply`, which loads and caches each collateral’s current `SpokeAssetConfig` [3](#0-2) . The cache returns a previously loaded config without rereading storage [4](#0-3) .

After the callback returns, the controller measures the collateral tokens sent back and calls `process_deposit` [5](#0-4) . `process_deposit` validates entry gates and fetches `require_spoke_asset`, but both paths consume the same stale `Context` cache rather than the current post-callback configuration [6](#0-5) .

Governance execution is permissionless once an operation is ready: `execute` accepts `executor: None`, invokes the scheduled controller call, and clears the scheduled state on success [7](#0-6) . Scheduled operations include `EditAssetInSpoke` and `RemoveAssetFromSpoke` [8](#0-7) .

### Impact Explanation

An attacker can borrow assets through `flash_position`, have their receiver execute a ready governance operation that removes or disables the collateral/debt market, and then have the controller finalize the position using the stale pre-callback admission and risk configuration.

Depending on the scheduled operation, this can leave debt collateralized by an asset that is no longer borrowable/collateralizable or no longer listed in the spoke, or by an asset whose LTV was just reduced. The resulting account can remain open because the post-callback checks only require nonzero debt and supply and finalize against the cached configuration [9](#0-8) .

This can cause protocol insolvency if the borrowed asset exceeds the collateral value admitted under the now-current risk parameters.

### Likelihood Explanation

Likelihood is conditional but does not require privileged execution at exploit time. A legitimate ready operation must exist that removes, pauses/freezes, or materially tightens the relevant spoke asset. Once such an operation is ready, any unprivileged address may execute it via governance `execute(None, ...)`, including from inside a flash receiver callback [10](#0-9) .

The attacker controls the receiver contract, callback timing, collateral return path, and account. The stale read is deterministic because the same `Context` is retained across the callback.

### Recommendation

Do not reuse spoke-asset admission/risk configuration across external callbacks.

At minimum:

- clear `Context::spoke_assets`, `spoke_config`, and related spoke verification caches after `invoke_receiver` returns, before `collect_collateral_deposits`, `process_deposit`, and `strategy_finalize`;
- or introduce `Context::refresh_after_external_call()` that drops all governance-controlled configuration while retaining only explicitly safe invocation-local accounting;
- additionally revalidate each collateral and debt asset against current storage immediately before final persistence.

The analogous fix to the Twig issue is to make the security/admission check run at the point it is relied on, not only when the `Context` entry was first populated.

### Proof of Concept

1. Governance has a ready `RemoveAssetFromSpoke` or `EditAssetInSpoke` operation for collateral asset `C` in spoke `S`.
2. Attacker calls:

   ```text
   flash_position(
       caller = attacker,
       account_id = 0,
       spoke_id = S,
       mode = Multiply,
       debt = D,
       amount = X,
       receiver = attacker_contract,
       data = encoded_ready_operation,
       collaterals = [(C, min_C)],
       refund_assets = []
   )
   ```

3. `flash_position` validates `C` and caches its still-listed `SpokeAssetConfig`.
4. The pool mints/forwards `X` units of `D` to `attacker_contract`.
5. During `execute_flash_position`, `attacker_contract`:
   - swaps or otherwise obtains `C`;
   - sends at least `min_C` of `C` to the controller;
   - calls governance `execute(None, controller, "remove_asset_from_spoke" | "edit_asset_in_spoke", args, predecessor, salt)` for the ready operation.
6. The callback returns. The controller measures the `C` balance increase and calls `process_deposit`.
7. `process_deposit` reads `C` from `Context::spoke_assets`, not from storage, so the removed or tightened current configuration is bypassed.
8. `strategy_finalize` evaluates the account using the stale cached risk configuration and persists an account with debt `D` and collateral `C` that should have been rejected or valued under the new configuration.

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L78-90)
```rust
    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    assert_with_error!(
        env,
        *receiver != pool_addr,
        FlashLoanError::InvalidFlashloanReceiver
    );
    // Caller-selected receivers require flash loans enabled; multiply uses
    // the configured router and does not require this flag.
    assert_with_error!(
        env,
        cache.cached_pool_sync_data(debt).params.is_flashloanable,
        FlashLoanError::FlashloanNotEnabled
```

**File:** contracts/controller/src/strategies/flash_position.rs (L145-154)
```rust
    let deposits = collect_collateral_deposits(env, &controller, collaterals, &collateral_before);
    process_deposit(env, &controller, &mut account, &deposits, &mut cache);

    refund_listed_assets(env, caller, refund_assets, &refund_before);

    // Check before and after finalization: its LTV refresh can prune zero-scaled
    // supply, and persistence removes empty accounts.
    require_flash_position_still_open(env, &account, debt);
    strategy_finalize(env, account_id, &mut account, &mut cache);
    require_flash_position_still_open(env, &account, debt);
```

**File:** contracts/controller/src/strategies/flash_position.rs (L192-214)
```rust
    for (hub_asset, min_amount) in collaterals.iter() {
        require_nonneg_amount(env, min_amount);
        assert_with_error!(
            env,
            !seen_assets.contains_key(hub_asset.asset.clone()),
            GenericError::InvalidPayments
        );
        if min_amount > 0 {
            has_positive_min = true;
        }
        require_can_supply(env, cache, account.spoke_id, &hub_asset);
        seen_assets.set(hub_asset.asset.clone(), true);
    }

    assert_with_error!(env, has_positive_min, StrategyError::CollateralRequired);

    validate_position_entry_gates(
        env,
        account,
        collaterals,
        cache,
        AccountPositionType::Deposit,
    );
```

**File:** contracts/controller/src/strategies/flash_position.rs (L297-322)
```rust
fn invoke_receiver(
    env: &Env,
    receiver: &Address,
    initiator: &Address,
    account_id: u64,
    asset: &Address,
    amount: i128,
    amount_received: i128,
    controller: &Address,
    data: &Bytes,
) {
    env.invoke_contract::<()>(
        receiver,
        &Symbol::new(env, "execute_flash_position"),
        (
            initiator.clone(),
            account_id,
            asset.clone(),
            amount,
            0i128,
            amount_received,
            controller.clone(),
            data.clone(),
        )
            .into_val(env),
    );
```

**File:** contracts/controller/src/context.rs (L191-204)
```rust
    /// Returns the listed spoke asset config, caching successful reads only.
    pub(crate) fn cached_spoke_asset(
        &mut self,
        spoke_id: u32,
        hub_asset: &HubAssetKey,
    ) -> Option<SpokeAssetConfig> {
        self.ensure_spoke_context(spoke_id);
        if let Some(cfg) = self.spoke_assets.get(hub_asset.clone()) {
            return Some(cfg);
        }
        let loaded = storage::get_spoke_asset(&self.env, spoke_id, hub_asset)?;
        self.spoke_assets.set(hub_asset.clone(), loaded.clone());
        Some(loaded)
    }
```

**File:** contracts/controller/src/positions/supply.rs (L100-135)
```rust
pub(crate) fn process_deposit(
    env: &Env,
    caller: &Address,
    account: &mut Account,
    aggregated: &AggregatedPayments,
    cache: &mut Context,
) {
    validate_position_entry_gates(
        env,
        account,
        aggregated,
        cache,
        AccountPositionType::Deposit,
    );
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
    for_each_leg(env, &entries, &results, |entry, result| {
        merge_supply_leg(env, account, &entry.action, &result, cache);
    });
```

**File:** contracts/governance/src/timelock/lifecycle.rs (L81-110)
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
}
```

**File:** contracts/governance/src/op.rs (L232-248)
```rust
        AdminOperation::EditAssetInSpoke(args) => {
            validate_spoke_asset(env, args);
            controller_operation(
                env,
                "edit_asset_in_spoke",
                vec![env, args.clone().into_val(env)],
            )
        }
        AdminOperation::RemoveAssetFromSpoke(args) => controller_operation(
            env,
            "remove_asset_from_spoke",
            vec![
                env,
                args.hub_asset.clone().into_val(env),
                args.spoke_id.into_val(env),
            ],
        ),
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
