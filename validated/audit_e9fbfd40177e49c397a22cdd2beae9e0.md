### Title
Unvalidated swap routes can inject unauthorized token transfers into the caller’s authorization tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The controller forwards caller-controlled `swap` bytes to the configured router during `swap_collateral`, `swap_debt`, `multiply`, and `repay_debt_with_collateral`. The controller bounds only the router’s measured spend and output, while route-selected downstream contracts can execute arbitrary calls beneath the caller’s authorization. A malicious route can therefore cause simulation to include an unrelated token transfer from the victim; if that authorization tree is signed, the transfer succeeds even though the strategy itself remains solvent. [1](#0-0) [2](#0-1) 

### Finding Description
`swap_collateral(caller, account_id, current, amount, new, swap)` accepts opaque route bytes and passes them through `process_swap_collateral` to `swap_tokens`. [3](#0-2) [4](#0-3) 

`swap_tokens` authorizes exactly one controller-to-router transfer, then invokes `execute_strategy(&controller, &amount_in, swap)`. Its post-call checks only reject input-balance growth, input overspending, and absent output; they do not constrain which contracts the route invokes or which unrelated authorizations those contracts request. [5](#0-4) 

The authorization helper creates an exact token `transfer` entry with no sub-invocations, but that protects only the controller’s contract authorization. The route bytes remain an untrusted instruction stream interpreted below the swap call. [6](#0-5) 

The repository’s auth-tree test demonstrates the result: a route-selected rogue hop records a victim-to-attacker token `transfer` as a child of the victim’s `swap_collateral` authorization. The fair swap output still arrives, so the strategy-level checks do not reveal or prevent the unrelated wallet transfer. [7](#0-6) 

### Impact Explanation
A malicious route can steal tokens held in the caller’s wallet in addition to consuming the intended routed collateral. The stolen amount is not bounded by the swap input, payload minimum output, controller balance checks, or final account-risk checks; the resulting position can remain healthy and deposit the expected fair output. [8](#0-7) [9](#0-8) 

### Likelihood Explanation
An unprivileged attacker can deploy a malicious contract and encode it as a route hop, then induce an account owner or delegate to submit a strategy using that route. The unauthorized transfer must appear in and be covered by the caller’s signed authorization tree; a wallet, transaction builder, AI assistant, or quote path that signs the simulated tree without validating its children enables the attack. [10](#0-9) 

### Recommendation
Do not allow route payloads to invoke arbitrary contracts beneath a strategy authorization. Enforce an on-chain governance-controlled venue allowlist or restrict route hops to known venue adapters and expected pool contracts. Independently, clients should reject any simulated authorization tree containing children other than the expected input-token transfer. [1](#0-0) [8](#0-7) 

### Proof of Concept
1. The attacker deploys a contract whose swap-like function calls `wallet_token.transfer(victim, attacker, victim_balance)`.
2. The attacker provides a `swap` payload that routes through that contract while returning enough output to satisfy the strategy.
3. The victim invokes `swap_collateral(caller, account_id, current, amount, new, swap)` or an equivalent strategy entrypoint.
4. The controller authorizes only its own exact input transfer and invokes the router with the attacker-controlled route bytes. [1](#0-0) 
5. Simulation records `wallet_token.transfer(victim, attacker, victim_balance)` as a child of the victim’s `swap_collateral` authorization. [2](#0-1) 
6. If the victim signs that simulated tree, the rogue contract transfers the wallet balance while the controller still receives and deposits fair swap output. [9](#0-8)

### Citations

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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L206-227)
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
}
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L230-269)
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
}
```

**File:** contracts/controller/src/lib.rs (L280-301)
```rust
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

**File:** common/src/token.rs (L33-51)
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
