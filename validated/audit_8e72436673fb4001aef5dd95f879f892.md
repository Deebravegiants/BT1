### Title
Untrusted swap-route code can add unauthorized wallet transfers to the caller’s Soroban authorization tree - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
Controller strategies accept an arbitrary XDR-encoded swap route and execute it through the configured router while the user’s authorization for the strategy remains active. [1](#0-0)  A malicious venue in that route can request a token transfer from the user to an attacker for an unrelated wallet asset, and Soroban simulation records that transfer as a child of the strategy authorization rather than rejecting it outright. [2](#0-1) [3](#0-2) 

### Finding Description
`swap_collateral`, `swap_debt`, `multiply`, and `repay_debt_with_collateral` all authenticate `caller` before forwarding the caller-selected `swap` payload into `swap_tokens` or `swap_tokens_or_passthrough`. [4](#0-3) [5](#0-4)  `swap_tokens` correctly limits the controller’s own invoker authorization to one exact input-token transfer to the configured router. [6](#0-5) 

That bound does not constrain a nested venue from separately calling `caller.require_auth()` through a token `transfer`. [7](#0-6)  The malicious transfer is represented as an additional child invocation under the user’s `swap_collateral` authorization, while the route can still return a fair output and satisfy the controller’s positive-output and final-risk checks. [8](#0-7) [9](#0-8)  The repository’s threat model explicitly confirms that such a child transfer executes when the caller signs the poisoned tree and that the loss is the caller’s wallet rather than merely the routed amount. [10](#0-9) 

### Impact Explanation
A malicious route can steal unrelated assets held directly by the user, not just the collateral amount intended for the strategy. [11](#0-10)  The swap may remain economically valid, so the strategy completes, deposits its expected output, and leaves the attack undetectable to the controller’s balance-delta checks for the strategy’s declared input and output tokens. [12](#0-11) 

### Likelihood Explanation
Exploitation requires the victim to submit a strategy containing attacker-selected route code and sign the authorization tree containing the extra token transfer. [13](#0-12)  A compromised or malicious frontend, route generator, wallet interface, or copied strategy payload can produce that tree while displaying only the ostensible lending operation. [14](#0-13)  Once signed, the unauthorized transfer executes inside the same transaction and cannot be mitigated by the controller’s post-swap accounting. [11](#0-10) 

### Recommendation
Do not allow arbitrary route-selected contracts to execute below an end-user-authorized lending strategy. [1](#0-0)  Governance should restrict route venues to audited, allowlisted contracts, or strategies should execute through an intermediate contract authorization model that prevents downstream venues from attaching requests to the end user’s credentials. [10](#0-9)  Until such a boundary exists, wallets and integrators must decode every route and reject any signed authorization tree containing children other than the exact expected token transfer. [14](#0-13) 

### Proof of Concept
1. Deploy a venue contract whose `swap` method calls `token.transfer(victim, attacker, victim_balance)` for a token unrelated to the swap. [15](#0-14) 
2. Construct a `swap_collateral` route that reaches this venue but returns enough of the destination collateral to satisfy `received > 0` and final solvency. [16](#0-15) 
3. Have the victim submit `swap_collateral(caller=victim, account_id, current, amount, new, swap=malicious_route)`. [17](#0-16) 
4. Simulation records the unrelated wallet-token transfer as a child invocation below the victim’s `swap_collateral` authorization. [2](#0-1) [9](#0-8) 
5. If the victim signs that recorded tree, the venue receives authorization for the transfer, drains the specified wallet balance, and still allows the nominal collateral swap to complete. [11](#0-10) [18](#0-17)

### Citations

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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L54-70)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L195-203)
```rust
fn simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry() {
    let s = Scene::new();
    let route = s.route_through_pool_stealing(WALLET_BALANCE);

    // `simulateTransaction` runs recording mode with non-root auth disabled.
    s.t.env.mock_all_auths();
    s.try_swap(&route)
        .expect("recording mode accepts the route");
    let recorded = s.t.env.auths();
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L206-212)
```rust
    let stolen_transfer = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.wallet_token.clone(),
            symbol_short!("transfer"),
            (s.alice.clone(), s.attacker.clone(), WALLET_BALANCE).into_val(&s.t.env),
        )),
        sub_invocations: std::vec![],
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L214-222)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L224-226)
```rust
    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
    assert_eq!(s.t.supply_balance_raw(ALICE, "ETH"), FAIR_OUT_ETH);
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L230-245)
```rust
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L264-268)
```rust
    };
    s.try_swap_with_signed_tree(&rogue, core::slice::from_ref(&stolen_transfer))
        .expect("the poisoned tree authorizes the rogue transfer");
    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
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

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-47)
```rust
    require_authorized_caller(env, caller);

    assert_with_error!(env, current != new, GenericError::AssetsAreTheSame);
    config::require_hub_active(env, current.hub_id);
    require_positive_amount(env, from_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L55-76)
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

    let deposit_assets = vec![env, (new.clone(), swapped_amount)];
    supply::process_deposit(
        env,
        &env.current_contract_address(),
        &mut account,
        &deposit_assets,
        &mut cache,
    );

    strategy_finalize(env, account_id, &mut account, &mut cache);
```

**File:** contracts/controller/src/strategies/multiply.rs (L90-97)
```rust
    let swapped_collateral = swap_tokens_or_passthrough(
        env,
        caller,
        &debt.asset,
        swap_amount_in,
        &collateral.asset,
        swap,
    );
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
