### Title
Opaque swap routes can place attacker-controlled code beneath the caller’s authorization and steal unrelated wallet tokens - ([File: contracts/controller/src/strategies/swap.rs])

### Summary
**High.** `swap_collateral`, `swap_debt`, and `repay_debt_with_collateral` accept an opaque route, authorize the controller-to-router input transfer, and invoke the configured aggregator while the caller’s authorization remains the transaction root. A malicious route can therefore put attacker-controlled venue code below that authorization and cause a token transfer from the caller to an attacker. [1](#0-0) [2](#0-1) 

### Finding Description
The affected controller entrypoints first authorize `caller`, then verify that `caller` owns or delegates the target account. `swap_collateral` subsequently withdraws collateral and calls the router through `withdraw_and_swap_from_supply`. [3](#0-2) [4](#0-3) [5](#0-4) 

The controller correctly scopes its own invoker authorization to one exact `token_in.transfer(controller, router, amount_in)`, but it still delegates execution of the supplied route bytes to the aggregator. [6](#0-5) 

The aggregator treats every swap hop’s `pool` as an opaque `Address` from the caller-supplied asset registry and dispatches it to a venue adapter; route decoding range-checks the address index but does not bind that address to a canonical pool, factory, or allowlist. [7](#0-6) [8](#0-7) [9](#0-8) 

Because that attacker-selected contract executes below the caller-authorized controller invocation, any `token.transfer(victim, attacker, amount)` it performs is represented as a child authorization under the caller’s signed invocation tree. [10](#0-9) 

The protocol’s balance-delta and positive-output checks constrain only the router’s custody and the swap’s declared input/output assets; they do not enumerate or reject unrelated transfers added to the caller’s authorization tree. [11](#0-10) [12](#0-11) 

### Impact Explanation
An attacker can steal tokens held directly by the victim that are unrelated to the lending position and outside the routed input amount. The measured-input guard bounds only controller-to-router spending, while the unrelated transfer is authorized by the victim’s transaction authorization tree. [13](#0-12) [14](#0-13) 

The same exposure applies to `swap_debt` and `repay_debt_with_collateral`, because both call the same `swap_tokens_or_passthrough` / `swap_tokens` boundary with caller-supplied route bytes. [15](#0-14) [16](#0-15) 

### Likelihood Explanation
An unprivileged attacker can deploy a contract implementing the selected venue adapter’s call interface, place its address in the route’s pool field, and make it steal an unrelated token before returning enough declared output to satisfy the route checks. [2](#0-1) [9](#0-8) 

Execution requires the victim to submit a poisoned route and sign the expanded authorization tree. This makes exploitation dependent on a malicious quote, phishing path, compromised route builder, or a client that does not reject unexpected child authorizations, but it does not require protocol privileges, leaked keys, or control of the aggregator owner. [17](#0-16) [18](#0-17) 

### Recommendation
Do not allow strategy payloads to name arbitrary executable venue contracts. Bind every hop’s `pool` to governance-approved or canonical venue/factory-derived addresses, or have each adapter verify the pool against the venue’s trusted registry before invoking it. [2](#0-1) [8](#0-7) 

As defense in depth, lending and aggregator clients must decode both the route and the simulated authorization tree and reject any child authorization other than the expected strategy token pulls. An honest composed controller strategy should produce only the controller’s exact input-transfer authorization; an unrelated `victim -> attacker` child must make signing fail closed. [19](#0-18) [10](#0-9) 

### Proof of Concept
1. Deploy `RoguePool` with a compatible venue entrypoint. On invocation, it calls `wallet_token.transfer(victim, attacker, wallet_balance)`, then performs or returns a nominally valid swap output.
2. Construct a route whose `assets` registry contains `RoguePool`, the expected `token_in`, and the expected `token_out`, with one swap operation selecting that pool.
3. Alice invokes `swap_collateral(alice, account_id, current_asset, amount, new_asset, route)`.
4. The controller authenticates Alice, withdraws `amount`, authorizes exactly `token_in.transfer(controller, router, amount)`, and invokes the router. [4](#0-3) [6](#0-5) 
5. The router decodes the attacker-selected pool address and invokes the venue adapter for that opaque address. `RoguePool` requests the unrelated wallet-token transfer from Alice. [7](#0-6) [9](#0-8) 
6. Simulation records `wallet_token.transfer(alice, attacker, wallet_balance)` as a child of Alice’s `swap_collateral` authorization; signing that tree makes the transfer execute while the strategy can still meet its output checks. [10](#0-9) [18](#0-17)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L24-54)
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

**File:** contracts/swap-aggregator/src/types.rs (L21-30)
```rust
/// One pool hop: swaps `token_in` for `token_out` through `venue`.
///
/// Built per instruction from registry indices; venue adapters consume this.
#[derive(Clone, Debug)]
pub struct SwapHop {
    pub pool: Address,
    pub token_in: Address,
    pub token_out: Address,
    pub venue: SwapVenue,
}
```

**File:** contracts/controller/src/lib.rs (L283-302)
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
        strategies::swap_collateral::process_swap_collateral(
            &env,
            &caller,
            SwapCollateralParams {
                account_id,
                current: &current,
                from_amount: amount,
                new: &new,
                swap: &swap,
            },
        );
```

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

**File:** contracts/swap-aggregator/src/execute/mod.rs (L152-165)
```rust
        Opcode::Swap(venue) => {
            let hop = SwapHop {
                pool: ctx.assets.get_unchecked(op.idx_a),
                token_in: ctx.assets.get_unchecked(op.idx_b),
                token_out: ctx.assets.get_unchecked(op.idx_c),
                venue,
            };
            let amount_in = resolve_amount(ctx, vault, op.mode, &hop.token_in, prev);
            if amount_in <= 0 {
                panic_with_error!(ctx.env, Error::InvalidAmount);
            }

            vault.withdraw(&hop.token_in, amount_in);
            let out = venues::dispatch_hop(ctx.env, ctx.router, &hop, amount_in, tokens_cache);
```

**File:** contracts/swap-aggregator/src/program.rs (L281-291)
```rust
            if idx_a >= assets_len || idx_b >= assets_len {
                panic_with_error!(env, Error::InvalidRouteXdr);
            }
            match opcode {
                Opcode::Swap(_) => {
                    if idx_c >= assets_len {
                        panic_with_error!(env, Error::InvalidRouteXdr);
                    }
                    if idx_b == idx_c {
                        panic_with_error!(env, Error::SameToken);
                    }
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

**File:** contracts/swap-aggregator/src/venues/mod.rs (L50-56)
```rust
    let after_in = ctx.input_balance();
    let spent = before_in
        .checked_sub(after_in)
        .unwrap_or_else(|| panic_with_error!(env, Error::InvalidAmount));
    if spent != amount_in {
        panic_with_error!(env, Error::InvalidAmount);
    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L166-183)
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
    }
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

**File:** contracts/controller/src/strategies/swap_debt.rs (L65-72)
```rust
    let repay_amount = swap_tokens_or_passthrough(
        env,
        caller,
        &new_debt.asset,
        amount_received,
        &existing_debt.asset,
        swap,
    );
```

**File:** contracts/controller/src/strategies/repay_debt_with_collateral.rs (L68-78)
```rust
    } else {
        repay_via_collateral_swap(
            env,
            caller,
            &mut account,
            &mut cache,
            collateral,
            collateral_amount,
            debt,
            swap,
        );
```
