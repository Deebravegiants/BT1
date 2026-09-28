### Title
Unallowlisted route venues can attach arbitrary token transfers to the caller’s authorization - (File: contracts/swap-aggregator/src/execute/mod.rs)

### Summary

A user-supplied swap route can place attacker-controlled pool code inside a `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, or direct `execute_strategy` call. The router does not allowlist the route’s pool address. A malicious venue can therefore request an unrelated `token.transfer(victim, attacker, amount)` while the victim’s root authorization is active. Transaction simulation records that transfer as a child of the victim’s authorization; if the victim signs the returned authorization tree, the malicious transfer succeeds while the declared swap still satisfies its output checks.

### Finding Description

`execute_strategy` accepts a fully caller-controlled `StrategyPayload` and only requires `sender.require_auth()` before decoding and executing it. For a swap operation, `pool`, `token_in`, and `token_out` are all selected from the caller-controlled `assets` vector, with no venue or pool allowlist. [1](#0-0) [2](#0-1) 

The Aquarius adapter calls `pool.get_tokens()` and then invokes the payload-selected pool’s `swap` function directly. [3](#0-2) [4](#0-3)  The surrounding router authorizes only its own `token_in.transfer(router, pool, amount_in)`, but that does not prevent the selected pool from initiating another token transfer using the caller’s ambient authorization. [5](#0-4) 

The controller paths expose the same route to users. `swap_collateral` authenticates the account owner or delegate and forwards the supplied `StrategySwap` into `withdraw_and_swap_from_supply`, which reaches `swap_tokens`. [6](#0-5)  `swap_tokens` invokes the configured router with the caller-controlled route and authorizes one exact router input transfer. [7](#0-6) 

The repository’s regression test demonstrates the authorization behavior: simulation records an attacker pool’s `token.transfer(victim, attacker, wallet_balance)` as a child invocation under the victim’s `swap_collateral` authorization, and enforcing mode executes it when the victim signs that tree. [8](#0-7) [9](#0-8) 

### Impact Explanation

This is theft of user funds beyond the declared swap input. The malicious venue can transfer any token balance or other authorization-compatible asset belonging to the victim, limited only by the victim’s signed authorization tree and token contract rules. The router’s balance-delta checks constrain only the router’s `token_in` spend and measured `token_out`; they do not bound unrelated transfers from the caller. The protocol documentation explicitly notes that this loss is the caller’s wallet, not the routed amount, and is not bounded by the declared minimum output or final account risk check. [10](#0-9) 

The result satisfies the theft-of-user-funds impact class. Severity should be High rather than Critical because the attacker must induce the victim to submit and sign a poisoned route and authorization tree; it cannot execute entirely without victim authorization.

### Likelihood Explanation

An unprivileged attacker can deploy a malicious pool contract and publish or inject a route that resolves to it. The malicious pool only has to satisfy the venue ABI and the router’s balance measurements: pull the authorized input, pay a positive output to the router, and request the extra transfer from the victim. Simulation then presents the extra token transfer as a child of the victim’s authorization.

The main precondition is that the victim’s client signs the simulation result without rejecting unexpected child authorization entries. The project’s own threat model places that obligation on the client, but the contract itself neither restricts the pool address nor constrains the authorization tree to the expected input transfer. [10](#0-9) 

### Recommendation

Do not allow arbitrary pool addresses in production routes. Maintain a governance-controlled venue/pool registry and validate every hop before execution, or bind routes to immutable venue adapter contracts that cannot be supplied as arbitrary account-level assets.

Additionally, require the transaction-building boundary to assert the exact expected authorization tree:

- Direct `execute_strategy`: only `token_in.transfer(sender, router, total_in)` may appear.
- Controller strategies: no unrelated caller-funded child invocation may appear; the controller’s router grant should be the only transfer authorization relevant to the swap.
- Wallets and frontends should fail when simulation returns any extra child authorization.

If arbitrary pools remain supported, the contract-level hazard should be treated as an explicit security boundary rather than only a client integration requirement.

### Proof of Concept

1. Deploy a malicious `RoguePool` whose `get_tokens()` returns `[token_in, token_out]`.
2. Give `RoguePool` a `swap(user, in_idx, out_idx, in_amount, out_min) -> u128` implementation that:
   - calls `token_in.transfer(router, pool, in_amount)` under the router’s invoker authorization;
   - calls `victim_token.transfer(victim, attacker, victim_balance)`;
   - transfers a positive amount of `token_out` to the router;
   - returns a nonzero value.
3. Have the victim call `controller.swap_collateral(caller, account_id, current, from_amount, new, swap)` or the direct `router.execute_strategy(sender, total_in, payload)` with a `StrategyPayload` selecting `RoguePool` as the hop pool.
4. Simulate the transaction. The rogue `victim_token.transfer(victim, attacker, victim_balance)` is recorded as a child of the victim’s authorization.
5. Sign and submit the returned authorization tree. The swap can still pass positive-output and input-spend checks, while the victim’s unrelated token balance is transferred to the attacker.

This exact authorization-tree behavior is implemented in `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`, where the signed poisoned tree results in the victim wallet balance becoming zero and the attacker receiving the full balance. [11](#0-10)

### Citations

**File:** contracts/swap-aggregator/src/execute/mod.rs (L51-66)
```rust
pub(crate) fn run(env: Env, sender: Address, total_in: i128, payload: StrategyPayload) -> i128 {
    sender.require_auth();

    if total_in <= 0 {
        panic_with_error!(&env, Error::InvalidAmount);
    }

    let StrategyPayload {
        amounts,
        assets,
        ops,
    } = payload;
    let program = Program::decode(&env, &ops, assets.len(), amounts.len());

    let input_token = assets.get_unchecked(program.token_in);
    let output_token = assets.get_unchecked(program.token_out);
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L151-166)
```rust
    match op.opcode {
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
```

**File:** contracts/swap-aggregator/src/venues/aquarius/swap.rs (L11-24)
```rust
pub(crate) fn swap(ctx: &HopContext<'_>, cache: &mut Map<Address, Vec<Address>>) {
    let tokens = pool_tokens(ctx.env, cache, &ctx.hop.pool);
    let in_idx = find_index(ctx.env, &tokens, &ctx.hop.token_in);
    let out_idx = find_index(ctx.env, &tokens, &ctx.hop.token_out);

    invoke_pool_swap(
        ctx.env,
        ctx.router,
        &ctx.hop.pool,
        &ctx.hop.token_in,
        in_idx,
        out_idx,
        ctx.amount_in,
    );
```

**File:** contracts/swap-aggregator/src/venues/aquarius/pool.rs (L25-35)
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
}
```

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

**File:** contracts/controller/src/strategies/swap.rs (L24-38)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L239-268)
```rust
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
