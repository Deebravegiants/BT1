### Title
Malicious swap routes can inject unauthorized token transfers into the caller’s signed authorization tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
Controller strategy entrypoints accept an opaque route payload and forward it to the configured swap router while the account owner or delegate’s top-level authorization is active. If route execution reaches attacker-controlled venue code, that code can request a token transfer from the caller; Soroban records the transfer as a sub-invocation beneath the caller’s strategy authorization. A client that signs the simulated tree without rejecting unexpected child invocations authorizes theft of wallet funds unrelated to the lending position.

### Finding Description
The controller accepts caller-supplied `swap` bytes through strategy entrypoints such as `swap_collateral`, `swap_debt`, `multiply`, and `repay_debt_with_collateral`. For example, `process_swap_collateral` first requires caller authorization and then forwards the route through `withdraw_and_swap_from_supply`. [1](#0-0) 

The router boundary authorizes only the controller’s exact input-token transfer, but it does not decode or constrain which contracts the payload causes the router to invoke. [2](#0-1) 

The harness demonstrates that a route-named pool can call `token.transfer(victim, attacker, amount)` while executing under the strategy call. In recording mode, that transfer is attached as a child of the victim’s `swap_collateral` authorization; when the victim signs the resulting poisoned tree, the wallet-token transfer executes and the strategy still completes. [3](#0-2) [4](#0-3) [5](#0-4) 

### Impact Explanation
An attacker can steal arbitrary tokens held by the victim’s wallet, beyond the collateral amount intentionally routed through the strategy. The measured router input/output and final account-risk checks do not bound this loss because the malicious transfer moves funds directly from the victim under a separately recorded authorization child.

### Likelihood Explanation
The attacker needs the victim to submit or sign a malicious route and the simulated authorization tree containing the extra transfer. This can occur through a compromised quote source, malicious frontend, deceptive route payload, or a client that treats simulator-produced authorization trees as safe. No protocol privilege, leaked key, governance action, or contract upgrade is required.

### Recommendation
Do not rely solely on post-call balance checks at the controller boundary. Establish a venue allowlist or otherwise constrain destination contracts reachable through route payloads. Clients must additionally decode routes and reject any simulated authorization tree containing children other than the expected controller strategy flow or the exact router input transfer. Surface unexpected sub-invocations as a hard signing failure rather than relying on users to inspect low-level authorization trees.

### Proof of Concept
1. The victim holds `WALLET_BALANCE` of a token that is not part of the lending position.
2. The attacker deploys a route destination whose swap entrypoint calls `token::Client::transfer(victim, attacker, WALLET_BALANCE)`.
3. The victim calls `swap_collateral` using a route that reaches this destination.
4. Simulation records the wallet-token transfer as a sub-invocation under the victim’s `swap_collateral` authorization.
5. If the victim signs that recorded tree, enforcement mode accepts the child transfer, moves the full wallet balance to the attacker, and still credits the expected swap output. The included regression test demonstrates both the poisoned authorization tree and the resulting balance changes.

### Citations

**File:** contracts/controller/src/strategies/swap_collateral.rs (L27-65)
```rust
pub(crate) fn process_swap_collateral(
    env: &Env,
    caller: &Address,
    params: SwapCollateralParams<'_>,
) {
    let SwapCollateralParams {
        account_id,
        current,
        from_amount,
        new,
        swap,
    } = params;

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

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
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
