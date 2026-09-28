### Title
Attacker-supplied route XDR runs arbitrary contract code inside the caller's authorization tree, stealing the swap caller's wallet funds - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The Batik flaw is "untrusted document reaches a code-execution primitive in the victim's trust context" (CWE-918/attacker-controlled content → Java execution). The lending analog: `swap_collateral`, `swap_debt`, `repay_debt_with_collateral` and `multiply` accept a caller-supplied `swap: Bytes` route and hand it verbatim to the router, which calls the pool/token addresses the payload names with **no venue or token allowlist**. A hop "pool" is attacker-deployed code running below the caller's `require_auth` tree. Any `token.transfer(caller, attacker, x)` it issues is recorded by simulation as a child of the caller's authorization entry and executes if the caller signs the simulated tree — draining wallet tokens the protocol never listed.

### Finding Description
`swap_tokens` in `contracts/controller/src/strategies/swap.rs` authorizes one exact `token_in.transfer(controller, router, amount_in)` and calls `router.execute_strategy(controller, amount_in, swap)` with the unvalidated route bytes. It guards only the controller's own balances (`RouterOverspend`, `NoSwapOutput`) and wraps the call in `with_flash_guard`, which blocks re-entry into the controller but does nothing about code the route executes.

Per `docs/reference/invariants.md` (INV-STRAT-01/02) and `docs/explanation/threat-model.md`, the router "calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization. A token transfer that such code makes from the caller is recorded by an honest simulation as a child of the caller's authorization entry, and it executes if the caller signs that tree. The loss is then the caller's wallet, not the routed amount, and neither the payload minimum nor the final risk gate bounds it." [1](#0-0) 

The harness test `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` proves the full path: a victim calls `swap_collateral` with a route whose `hop_pool` is `RogueHopPool`, whose `swap()` executes `token::Client::transfer(alice → attacker, WALLET_BALANCE)` on an unlisted token. Simulation records the theft as a sub-invocation of the victim's `swap_collateral` auth entry; the honest root-only tree is rejected by the host, but the poisoned simulated tree, once signed, moves the full wallet balance. [2](#0-1) [3](#0-2) 

### Impact Explanation
Theft of user funds: arbitrary tokens in the caller's wallet (not just the routed `amount_in`, and not just protocol-listed assets) can be transferred to the attacker when the victim signs the auth tree the route produces. The controller's measured-output check passes because the rogue pool returns a fair swap output; the theft rides alongside an economically honest swap, so no on-chain gate detects it. Bounded only by the victim's wallet contents and their willingness to sign a simulated tree.

### Likelihood Explanation
Requires a victim to submit a transaction carrying an attacker-authored route (phished UI, compromised quote feed, or a malicious `routeXdr`) and to sign the auth tree Soroban simulation returns. Common wallet flows sign the simulated tree verbatim, so the poisoned child entry is presented for signature automatically. An unprivileged attacker needs only to deploy a contract and get the route in front of a user; no protocol privilege is involved. The user-signing precondition and detectable auth tree keep this below Critical/High.

### Recommendation
This is the same defense the Batik fix applied (restrict what untrusted input may invoke):
- Maintain a governance-approved venue/pool allowlist (mirroring `INV-STRAT-03`'s Blend pool approval) and have the router or controller reject hops to unlisted pool addresses.
- Absent an allowlist, document and enforce at the controller that routes may only reference tokens listed in the relevant hub and pools registered per (token pair).
- Client-side hard stop (already noted in the threat model): signers must decode the route and reject any authorization tree containing sub-invocations beyond the single expected `token_in.transfer`.

### Proof of Concept
Executable harness PoC exists: `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`. `RogueHopPool::swap` (lines 62–71) transfers `WALLET_BALANCE` of an unlisted token from Alice to the attacker. `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` shows the theft nested inside Alice's `swap_collateral` auth and her balance going to 0; `enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer` shows signing the simulated tree completes the drain while the fair 2.5 ETH swap output still settles.

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
