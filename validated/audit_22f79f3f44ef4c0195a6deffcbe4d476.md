### Title
User-supplied swap route lets arbitrary "pool" contracts execute under the caller's authorization tree and drain the caller's wallet - ([File: contracts/swap-aggregator/src/execute/mod.rs])

### Summary
The bug class in the reference report is "untrusted, attacker-controlled input is handed to a primitive that executes what it names" (`QDesktopServices::openUrl` executing a `nc://open/` path). The analog here is the swap route payload: `execute_strategy` decodes caller-supplied `assets`/`ops` and invokes whatever contract address the payload names as a `pool`, with no venue or pool allowlist. A malicious pool runs arbitrary code on the call stack beneath the caller's `require_auth` entry, and any `token.transfer(victim, attacker, x)` it makes is recorded as a child of the caller's signed auth tree — draining tokens far beyond the routed amount.

### Finding Description
`execute_op` resolves `hop.pool` directly from the caller-controlled `assets` registry (`ctx.assets.get_unchecked(op.idx_a)`) and passes it to `venues::dispatch_hop`, which performs `env.invoke_contract(&hop.pool, "swap", ...)` (e.g. `sushi.rs` lines 48–50, `comet.rs` lines 30–34). There is no allowlist of pool or token addresses: the threat-model doc states "The router calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization" [1](#0-0) . The test `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` demonstrates a `RogueHopPool` whose `swap` calls `token.transfer(victim, attacker, WALLET_BALANCE)`; recording-mode simulation attaches that transfer as a child of Alice's `swap_collateral` auth entry and, once signed/enforced, the transfer executes — Alice's unrelated wallet token balance goes to zero while she still receives her "fair" swap output [2](#0-1) .

The reachable entrypoints are the controller strategy paths that accept a raw `swap`/`StrategySwap` payload from an unprivileged caller — `swap_collateral`, `swap_debt`, `multiply`, `repay_debt_with_collateral` — each of which forwards the caller's bytes to `router.execute_strategy` in `swap_tokens` [3](#0-2) , plus direct `execute_strategy` calls on the router.

### Impact Explanation
Theft of user funds. The stolen amount is not bounded by `total_in`, by `min_out`, or by the controller's balance-delta checks (`RouterOverspend`, `NoSwapOutput`) — those only measure the controller's own balances [4](#0-3) . The rogue pool can transfer any token the victim holds, in full, because the victim's signature on the simulated auth tree legitimately covers the injected child invocation. This mirrors the reference bug: the victim merely clicks a link / signs a route that appears to produce a correct result while the untrusted input names code that executes against their assets.

### Likelihood Explanation
Exploitation requires a victim to submit an attacker-crafted route payload (e.g. via a malicious frontend, phishing quote, or a compromised quote server response the user does not re-verify). The attacker is fully unprivileged: they only need to deploy a contract and convince the victim to sign the transaction. Standard wallets/clients that sign the simulation-produced auth tree without decoding it will sign the poisoned tree. The threat model itself flags the direct `execute_strategy` path as having "the same exposure for every swap user" [5](#0-4) .

### Recommendation
Analogous to the report's fix (don't pass untrusted input to `openUrl`; verify a token / restrict to safe targets):

- Maintain an on-chain allowlist (or registry-hash allowlist) of venue pool addresses and token addresses that routes may reference, populated by governance; reject payload indices resolving to non-listed addresses before any `invoke_contract`.
- Alternatively, pin each venue opcode to factory-verified pools (e.g. query the venue factory / `share_id` validation as Aquarius already does via `assert_share_token`) so a payload cannot name an arbitrary contract.
- At minimum, have the controller enforce a strict structural check on the caller's required auth tree shape (exactly one input `transfer` child) and document/enforce the same for direct router users, since the current design outsources this check to every client [6](#0-5) .

### Proof of Concept
See `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`:

1. Attacker deploys `RogueHopPool` whose `swap()` executes `token.transfer(alice, attacker, WALLET_BALANCE)` on an arbitrary token Alice holds [7](#0-6) .
2. Attacker crafts a `swap_collateral(alice, account_id, USDC, amount, ETH, route)` where `route.assets` names the rogue contract as the hop pool.
3. Alice's client simulates; recording mode returns an auth tree containing the theft `transfer` as a child of her `swap_collateral` entry; she signs it.
4. On execution the swap delivers the expected ETH output and the rogue pool simultaneously moves Alice's entire `WALLET_BALANCE` to the attacker — asserted at lines 224–226 [8](#0-7) .

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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-226)
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
```

**File:** contracts/controller/src/strategies/swap.rs (L36-38)
```rust
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
