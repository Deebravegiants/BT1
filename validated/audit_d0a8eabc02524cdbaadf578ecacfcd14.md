### Title
Attacker-crafted `swap_xdr` route executes arbitrary contract code under the caller's signed authorization tree, draining tokens beyond the routed amount - ([File: contracts/controller/src/strategies/swap.rs])

### Summary
Analog of CVE-2021-30124 (a crafted configuration value is executed as a command): an attacker supplies a crafted `StrategySwap`/route XDR payload, and the controller hands it verbatim to the swap router, which invokes whichever "pool" contracts the payload names — with no venue/token allowlist. Because the victim's `require_auth` on `swap_collateral`/`swap_debt`/`repay_debt_with_collateral`/`multiply` is the only signature in play, a rogue pool inside the route can issue `token.transfer(victim, attacker, x)` and that invocation is recorded as a child of the victim's own authorization entry, so it executes once the victim signs the simulated tree. The in-repo test `rogue_hop_pool_transfer_joins_caller_auth_tree.rs` demonstrates a victim's entire balance of an unrelated token being transferred to the attacker this way.

### Finding Description
`swap_tokens` in `contracts/controller/src/strategies/swap.rs` takes the caller-supplied `swap: &StrategySwap` bytes, performs no decoding or validation of the venues it references, and calls `router.execute_strategy(&controller, &amount_in, swap)` after authorizing only the exact input transfer [1](#0-0) . The router decodes the payload and dispatches each hop to a venue adapter keyed by a `pool` address taken straight from the caller-controlled `assets` registry — there is no allowlist of pools, tokens, or venues [2](#0-1) . The controller's post-conditions only check its own input spend and positive output (`RouterOverspend`, `NoSwapOutput`) [3](#0-2) ; nothing constrains what the named pool contract does while on the stack beneath the caller's authorization.

The threat model itself states the consequence: "The router calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization. A token transfer that such code makes from the caller ... executes if the caller signs that tree. The loss is then the caller's wallet, not the routed amount" [4](#0-3) . The regression test confirms it end-to-end: a `RogueHopPool.swap` issues `token::Client::transfer(victim, attacker, amount)` and simulation records it as a sub-invocation of the victim's `swap_collateral` auth entry; Alice's full wallet balance moves to the attacker while the swap itself settles normally [5](#0-4) . The test's own router double shows that any router/pool implementation honoring the payload's named addresses enables this — and the production router keeps no allowlist, so any venue adapter that invokes the payload-named `pool` (Aquarius, Soroswap, Phoenix, Sushi, Comet) gives the attacker a call frame.

### Impact Explanation
Theft of user funds. A victim who submits `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, `multiply`, or `flash_position` with an attacker-supplied route (e.g., a malicious `routeXdr` obtained from a compromised/typosquatted quote source or phishing) signs an authorization tree containing `transfer(victim → attacker)` for arbitrary tokens the protocol never touches. The protocol's own bounds — measured input spend, positive output, min-out, final risk gates — all pass, because the theft rides on the victim's signature rather than protocol custody. Loss is bounded only by the victim's wallet balances, not by the routed amount.

### Likelihood Explanation
High reachability for the crafting primitive (any unprivileged address can encode arbitrary pool addresses in `assets` and name them in a hop), but exploitation requires inducing a victim to sign a poisoned auth tree. Honest clients that decode the route and reject unexpected auth children mitigate it, and simulation exposes the extra sub-invocation — but nothing in the contracts prevents it, and the API/SDK flow explicitly expects users to consume externally generated `routeXdr` blobs. Medium-to-High likelihood; High severity overall given the unbounded wallet drain relative to routed amount.

### Recommendation
Constrain route execution so attacker-named contracts cannot run under the user's auth:

- Maintain a governance-managed allowlist of pool/venue contracts in the router (or pin venue adapters to registry-looked-up pool addresses rather than payload-supplied `Address` values), analogous to the Blend pool approval list in `AdminOperation::ApproveBlendPool`.
- In each venue adapter, resolve the pool address from the venue's own factory/registry where available instead of trusting `assets[idx_a]`.
- Defense in depth on the controller: after `execute_strategy`, require the victim-facing auth tree shape (impossible on-chain, so this must live in the SDK/quote server — but the contract-level fix is the allowlist).

### Proof of Concept
See `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`: deploy a `RogueHopPool` whose `swap()` does `token.transfer(victim, attacker, WALLET_BALANCE)`; encode a route naming that pool; call `controller.swap_collateral` as Alice. Simulation records the stolen transfer as a child of Alice's `swap_collateral` `AuthorizedInvocation`; signing that tree executes the transfer (`assert_eq!(recorded, vec![(alice, poisoned_root)])`, `wallet(alice) == 0`, `wallet(attacker) == WALLET_BALANCE`) while `supply_balance_raw(ALICE, "ETH")` shows the swap still completed [5](#0-4) .

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L34-38)
```rust
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```

**File:** contracts/controller/src/strategies/swap.rs (L42-54)
```rust
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

**File:** docs/explanation/threat-model.md (L154-163)
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
