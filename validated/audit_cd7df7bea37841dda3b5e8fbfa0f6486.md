### Title
Unallowlisted route venues let a crafted `swap_xdr` execute arbitrary contract code under the caller's authorization tree and drain the caller's wallet - (File: contracts/swap-aggregator/src/venues/mod.rs)

### Summary
The Jenkins CVE class — a crafted packet causing the server to run attacker-chosen code — maps directly onto the swap aggregator's route program: the `swap_xdr` bytes an unprivileged caller submits name the pool contract of every hop, and the router invokes those addresses with no allowlist. A crafted route places attacker-deployed code on the call stack below the victim's `require_auth`, where it can issue `token.transfer(victim, attacker, amount)` calls that Soroban's simulation records as children of the victim's own authorization entry. If the victim signs the simulated tree — the standard wallet flow — the transfer executes, moving wallet funds far beyond the routed amount. This affects `execute_strategy` directly and every controller strategy verb that forwards user-supplied `swap` bytes (`multiply`, `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`).

### Finding Description
`dispatch_hop` dispatches `hop.pool` to a fixed set of venue adapters, but `hop.pool` itself comes entirely from the caller-supplied packed program (`assets` registry, indexed by the instruction bytes) and is never validated against any allowlist [1](#0-0) . Each adapter then does `env.invoke_contract(&ctx.hop.pool, ...)` on that attacker-chosen address [2](#0-1) .

The threat model states the consequence plainly: the router "keeps no allowlist" of the pool and token addresses its payload names, "so a route can put third-party code on the call stack below the caller's authorization," and a token transfer that code makes from the caller "executes if the caller signs that tree," making the loss "the caller's wallet, not the routed amount," unbounded by either the payload `min_out` or the controller's final risk gates [3](#0-2) .

On the controller side, `swap_tokens` grants the router exactly one input-transfer authorization and then invokes `execute_strategy` inside the flash guard [4](#0-3) . The router's own balance-delta accounting (`RouterOverspend`, `NoSwapOutput`, `SlippageExceeded`) still passes, because the rogue pool can pay a fair output while stealing unrelated wallet tokens in the same call.

The harness test `rogue_hop_pool_transfer_joins_caller_auth_tree.rs` proves the full chain end-to-end: a router double invokes a `RogueHopPool` whose `swap` does `token.transfer(victim, attacker, WALLET_BALANCE)` [5](#0-4) ; recording mode attaches that transfer as a child of the victim's `swap_collateral` auth entry [6](#0-5) ; and in enforced mode the same route succeeds and empties the wallet when the victim signs the poisoned tree [7](#0-6) .

### Impact Explanation
Theft of user funds. The rogue hop contract can transfer any token the victim holds to an attacker address, with no upper bound related to the swap size — the test drains `WALLET_BALANCE` of a token the protocol never listed while the swap itself settles at a fair rate [8](#0-7) . More generally the crafted packet executes arbitrary contract code in the caller's auth context, matching CWE-94.

### Likelihood Explanation
Exploitation needs the victim to submit a route that names the attacker's contract — e.g., a route bytes payload served by a compromised/malicious quote source or a phishing frontend — and then sign the authorization tree simulation returns. Simulation automatically produces the poisoned tree, so a wallet that signs the simulated envelope without decoding the route signs the wallet-draining child entry [9](#0-8) . The defense is pushed entirely to clients ("a client must decode the route it signs"), which many integrations will not do. Unprivileged reach, real loss, but gated on tricking the signer — consistent with a Medium rating.

### Recommendation
Enforce a venue-address allowlist on-chain: maintain an owner-managed registry of approved pool contracts per venue and reject `hop.pool` addresses not registered for the declared `SwapVenue` inside `dispatch_hop` before `invoke_contract` [1](#0-0) . Additionally, bound each hop's side effects by asserting the victim's auth footprint: where feasible, have the router run the venue call such that any nested `require_auth` on the caller other than the single input `transfer` cannot be attached (e.g., performing the input pull itself and passing pre-transferred funds). Until an allowlist exists, SDK/wallet integrations should decode `swap_xdr` and refuse authorization trees containing any child beyond the documented input transfer [10](#0-9) .

### Proof of Concept
The committed test `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` is a working PoC. Concretely:

1. Attacker deploys a contract with a `swap` entrypoint that calls `token::Client::new(&env, &victim_token).transfer(&victim, &attacker, &amount)` — arbitrary code, any token, any amount [5](#0-4) .
2. Attacker ships a `swap_xdr`/`StrategyPayload` whose `assets` registry names the attacker's contract as the hop `pool` and whose `amounts[min_out]` is a fair output so all measured-delta checks pass.
3. Victim submits `controller.swap_collateral(victim, account_id, usdc_key, amount_in, eth_key, swap_xdr)` (or `execute_strategy` directly). `simulateTransaction` records the rogue `transfer` as a child under the victim's `swap_collateral` auth entry and returns the poisoned tree [11](#0-10) .
4. Victim's wallet signs the simulated envelope; in enforced mode the transfer executes: victim's wallet token balance goes to 0, attacker's to `WALLET_BALANCE`, while the victim still receives the fair `token_out` — so `min_out`, `RouterOverspend`, `NoSwapOutput`, and the post-swap health check all pass [12](#0-11) .

The benign control (rogue pool that steals nothing) passes with the honest root-only tree, confirming the authorization machinery is not the bug — the unallowlisted `hop.pool` invocation is [13](#0-12) .

### Citations

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

**File:** contracts/swap-aggregator/src/venues/comet.rs (L30-34)
```rust
    let _: (i128, i128) = ctx.env.invoke_contract(
        &ctx.hop.pool,
        &Symbol::new(ctx.env, "swap_exact_amount_in"),
        args,
    );
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

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L233-237)
```rust
    // Control: a pool that touches nothing passes with the honest root-only tree.
    let benign = s.route_through_pool_stealing(0);
    s.try_swap_with_signed_tree(&benign, &[])
        .expect("the honest tree authorizes an honest route");
    assert_eq!(s.wallet(&s.alice), WALLET_BALANCE);
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L258-269)
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
}
```
