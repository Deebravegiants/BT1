### Title
Attacker-controlled `flash_position` receiver can execute unauthorized token transfers beneath the caller’s authorization tree - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary

`flash_position` accepts an arbitrary deployed Wasm `receiver` and invokes it during the transaction while the caller’s authorization is active. A malicious receiver can request the caller’s authorization for an unrelated token transfer; transaction simulation records that transfer as a child of the caller’s `flash_position` authorization, and a signed tree containing that child executes it. This mirrors the Ghostscript unchecked implementation-pointer class: attacker-selected code executes under privileges granted for a different operation.

### Finding Description

The public entrypoint takes caller-controlled `receiver` and `data` arguments [1](#0-0) . `process_flash_position` authenticates only the caller, then requires the receiver to be a Wasm contract while rejecting only the controller and pool addresses [2](#0-1) .

The strategy mints debt, forwards it to that receiver, snapshots the declared balances, and invokes the receiver inside the flash guard [3](#0-2) . These balance checks constrain declared collateral and refund assets, but they do not constrain which authorization requests the receiver makes against the caller for unrelated assets [4](#0-3) .

The repository’s authorization-tree regression test demonstrates the same reachable shape through a route-selected contract: malicious callee code records `token.transfer(caller, attacker, amount)` beneath the caller’s root authorization, and enforcing mode executes it when that child is signed [5](#0-4) [6](#0-5) .

### Impact Explanation

An attacker can steal any token balance for which the victim signs the extra child authorization, including assets unrelated to the lending position and outside the protocol’s collateral/refund accounting [7](#0-6) . The normal flash-position settlement checks can still succeed because they measure only protocol-declared token deltas and final account risk, not every privilege consumed beneath the caller’s authorization root [4](#0-3) .

This is theft of user funds and can exceed the flash-position amount because the stolen token, recipient, and amount are selected by the malicious receiver [8](#0-7) .

### Likelihood Explanation

The attacker only needs to deploy a Wasm receiver and induce the victim to submit `flash_position` with that receiver and attacker-supplied `data`; no protocol privilege or leaked key is required [9](#0-8) . Simulation can present the malicious transfer as part of the transaction’s required authorization tree, so a wallet or compositional client that does not reject unexpected child invocations will produce a signature that executes it [10](#0-9) .

Likelihood is reduced because the victim’s signed authorization must include the malicious transfer; an honest tree that omits it is rejected by host authorization [11](#0-10) . This makes the issue a Medium-severity authorization-boundary weakness rather than an unauthenticated theft.

### Recommendation

Do not expose arbitrary callback execution underneath an account-authorizing entrypoint without constraining the authorization semantics expected by callers and clients. Prefer a design where the receiver is selected from a governance-approved set, or split the operation into separate transactions so collateral delivery cannot be bundled with unrelated caller authorizations [3](#0-2) .

If arbitrary receivers remain supported, SDKs and transaction builders must simulate the exact transaction, decode every authorization subtree, and reject any child invocation other than the explicit protocol/token calls the user requested [12](#0-11) . The contract should also document that `data` and `receiver` are adversarial and that balance-delta settlement does not bound unrelated caller authorization [13](#0-12) .

### Proof of Concept

1. The attacker deploys a Wasm receiver whose `execute_flash_position` callback performs `unrelated_token.transfer(victim, attacker, victim_balance)` and then transfers enough declared collateral to satisfy `collaterals` [14](#0-13) .
2. The attacker gives the victim a `flash_position(caller=victim, account_id, spoke_id, mode, debt, amount, receiver=malicious_receiver, data=attacker_data, collaterals, refund_assets)` call whose collateral minimum can be satisfied from the forwarded debt or attacker-controlled liquidity [1](#0-0) .
3. Simulation records the malicious token transfer as a child under the victim’s `flash_position` authorization rather than as a separate top-level authorization [10](#0-9) .
4. If the victim signs that returned tree, the malicious transfer executes, the declared collateral checks can pass, the position remains solvent, and the unrelated wallet token is transferred to the attacker [6](#0-5) [4](#0-3) .

### Citations

**File:** contracts/controller/src/lib.rs (L189-200)
```rust
    fn flash_position(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        mode: PositionMode,
        debt: HubAssetKey,
        amount: i128,
        receiver: Address,
        data: Bytes,
        collaterals: Vec<(HubAssetKey, i128)>,
        refund_assets: Vec<Address>,
```

**File:** contracts/controller/src/strategies/flash_position.rs (L45-84)
```rust
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

**File:** contracts/controller/src/strategies/flash_position.rs (L119-143)
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
            (amount_received, collateral_before, refund_before)
        });
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

**File:** contracts/controller/src/strategies/flash_position.rs (L171-215)
```rust
/// Validates collateral limits, supply eligibility and non-negative minimums
/// with at least one positive. Uniqueness is by token, since different hubs
/// share the same controller token balance.
fn validate_collaterals(
    env: &Env,
    cache: &mut Context,
    account: &Account,
    collaterals: &Vec<(HubAssetKey, i128)>,
) {
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
}
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L50-71)
```rust
/// Attacker-deployed "pool". `amount == 0` is the benign control.
#[contract]
pub struct RogueHopPool;

#[contractimpl]
impl RogueHopPool {
    pub fn __constructor(env: Env, victim: Address, token: Address, to: Address, amount: i128) {
        env.storage()
            .instance()
            .set(&symbol_short!("PLAN"), &(victim, token, to, amount));
    }

    pub fn swap(env: Env) {
        let (victim, wallet_token, to, amount): (Address, Address, Address, i128) = env
            .storage()
            .instance()
            .get(&symbol_short!("PLAN"))
            .expect("plan is set by the constructor");
        if amount > 0 {
            token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
        }
    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-227)
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
}
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L239-257)
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

```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L258-269)
```rust
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
}
```

**File:** docs/explanation/threat-model.md (L154-165)
```markdown
That bound covers the controller's own grant only. The router calls the pool
and token addresses its payload names and keeps no allowlist of them, so a
route can put third-party code on the call stack below the caller's
authorization. A token transfer that such code makes from the caller is
recorded by an honest simulation as a child of the caller's authorization
entry, and it executes if the caller signs that tree. The loss is then the
caller's wallet, not the routed amount, and neither the payload minimum nor the
final risk gate bounds it. An honest swap strategy gives the caller no child
entry, and a direct router swap gives exactly one input transfer. A client must
decode the route it signs and refuse an authorization tree with any other
child. The direct `execute_strategy` path has the same exposure for every swap
user.
```
