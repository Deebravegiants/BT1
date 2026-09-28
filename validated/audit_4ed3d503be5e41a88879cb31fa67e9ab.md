### Title
Unsanitized route bytes let a rogue venue inject a wallet-draining `transfer` under the caller's signed auth tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The XWiki bug class is "a user-controlled parameter reaches a privileged execution context without sanitization, enabling injected actions under authority the victim intended for something else." In XOXNO Lending the matching surface is the `swap: Bytes` argument on `multiply`, `swap_debt`, `swap_collateral` and `repay_debt_with_collateral`. Those bytes are a caller-supplied `StrategyPayload` program: indexed `assets` entries name arbitrary pool contracts, and the router invokes them with no venue allowlist. A malicious "pool" invoked mid-route can call `token.transfer(victim, attacker, wallet_balance)`, which the Soroban host records as a sub-invocation of the *victim's* authorization entry on the controller strategy call. If the victim signs the simulated auth tree (the standard wallet flow), the injected transfer executes, draining tokens far beyond the routed `amount_in`.

### Finding Description
`swap_tokens` in `contracts/controller/src/strategies/swap.rs` forwards the caller's `StrategySwap` bytes verbatim to `router.execute_strategy(&controller, &amount_in, swap)` inside a flash guard, and only measures the controller's `token_in`/`token_out` balance deltas afterward [1](#0-0) . Nothing on the controller side inspects which venue addresses the route names.

On the router side, `execute::run` decodes the packed program and `venues::dispatch_hop` invokes `ctx.hop.pool` — an address taken directly from the caller-supplied `assets` registry — so arbitrary third-party code executes on the call stack while the caller's auth entry is active (documented boundary: the router "keeps no allowlist" of pool addresses and "a route can put third-party code on the call stack below the caller's authorization") [2](#0-1) . Venue calls are self-authorized by the router, but nothing prevents the venue contract itself from requesting the *sender's* auth for an unrelated token `transfer`; the host records it as a child of the victim's `swap_collateral`/etc. entry.

The harness proves end-to-end reachability: `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` shows simulation emitting an auth tree containing `wallet_token.transfer(alice, attacker, WALLET_BALANCE)` under Alice's `swap_collateral` root, and `enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer` shows that signing that tree moves the entire wallet balance while the swap still settles normally [3](#0-2) .

### Impact Explanation
Theft of user funds. The loss is not bounded by `amount_in`, the payload's `min_out`, or the controller's `RouterOverspend`/`NoSwapOutput` checks — those only bound the routed input and measured output, while the injected transfer targets the victim's unrelated wallet balances in any token the victim holds. An unprivileged attacker can deploy a malicious contract, embed its address as a venue `assets` entry in a crafted `routeXdr`, and have it propagate through the quote/UX pipeline to victims. Every victim who signs the poisoned tree loses whatever the rogue venue pulls (any token, any amount it requests and the signer approves).

### Likelihood Explanation
Medium. Exploitation requires (a) a victim submitting an attacker-influenced `swap` payload on `multiply`/`swap_debt`/`swap_collateral`/`repay_debt_with_collateral` (or the direct router `execute_strategy` path, which shares the exposure), and (b) the victim signing an auth tree containing the extra sub-invocation. Wallets/flows that auto-sign simulated auth trees without diffing sub-invocations make (b) realistic, since the tree is produced by a successful simulation of a swap that genuinely settles. The attack needs no privilege, no oracle manipulation, and no timing window; the only mitigation is off-chain client diligence, which the threat model explicitly delegates to integrators rather than enforcing in the contract.

### Recommendation
Constrain the class the same way escaping would have: bind route venues to an allowlist. The router should check each `pool`/`token` address used by Swap/Burn/Mint instructions against a governance-managed venue allowlist (as `migrate_from_blend` already does for Blend pools via INV-STRAT-03), or the controller should require a hash/registry of approved venue addresses per strategy call. Until then, document at the ABI level that any non-empty `swap` payload must be decoded client-side and the transaction rejected if the signed auth tree contains any child other than the single expected input `transfer`.

### Proof of Concept
The repository already contains the working exploit test, `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`:

1. Attacker deploys a contract (`pool_stealing`) that, when invoked as a swap venue, calls `wallet_token.transfer(alice, attacker, WALLET_BALANCE)` using the caller's auth.
2. Attacker crafts a `routeThroughPoolStealing(WALLET_BALANCE)` `StrategyPayload` naming that contract as the hop pool and returns a fair-looking output so all settlement checks pass.
3. Alice submits `swap_collateral` with that route; simulation records the stolen transfer as a sub-invocation of her `swap_collateral` auth entry (`assert_eq!(recorded, vec![(alice, poisoned_root)])`).
4. With the signed (poisoned) tree, execution completes the swap (`supply_balance_raw(ALICE, "ETH") == FAIR_OUT_ETH`) and additionally yields `wallet(&alice) == 0`, `wallet(&attacker) == WALLET_BALANCE`.

The injected venue call is the direct analog of the unescaped `width` parameter: attacker-controlled data interpreted inside an authorization context broader than the caller intended.

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L33-54)
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-269)
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

#[test]
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
