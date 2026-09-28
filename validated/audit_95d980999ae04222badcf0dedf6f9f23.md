### Title
Attacker-controlled route bytes can inject a victim-authorized token transfer through `swap_collateral` - ([File: contracts/controller/src/strategies/swap.rs])

### Summary
The controller treats `swap` as opaque executable route data and forwards it to the configured router while constraining only the controller’s own input-token transfer. The router interprets caller-supplied address-registry entries as venue, token, and pool addresses without an on-chain venue allowlist. A malicious route can therefore place attacker-controlled code under the caller’s authorization tree and record an unrelated token transfer from the swapper to the attacker.

### Finding Description
`swap_collateral(caller, account_id, current, amount, new, swap)` authorizes the account owner or delegate, withdraws collateral, and passes the caller-supplied `swap` bytes into `swap_tokens`. [1](#0-0)  `swap_tokens` only self-authorizes the exact `token_in.transfer(controller, router, amount_in)` and then invokes `router.execute_strategy(controller, amount_in, swap)`. [2](#0-1)  The packed route maps instruction records onto an attacker-supplied `assets` registry; a swap instruction resolves its `pool`, `token_in`, and `token_out` from that registry and dispatches the named venue. [3](#0-2) [4](#0-3) 

The route decoder validates byte length, opcode values, index bounds, token-chain shape, and split weights, but it does not establish that `assets[idx_a]` is an authentic DEX pool. [5](#0-4)  Venue adapters then invoke the payload-selected pool address—for example, Phoenix `swap` calls `invoke_contract(&ctx.hop.pool, "swap", args)`. [6](#0-5)  During that invocation, the malicious pool can make a token call that requires the swapper’s authorization. Simulation records it as a child invocation beneath the caller’s `swap_collateral` authorization, and the transfer executes if the caller signs the poisoned tree. [7](#0-6) 

### Impact Explanation
A crafted route can steal unrelated tokens from the swapper’s wallet, beyond the collateral amount intentionally routed through the strategy. The harness reproduction records a child `transfer(alice, attacker, WALLET_BALANCE)` beneath Alice’s `swap_collateral` authorization; after signing that tree, Alice’s unrelated wallet-token balance is zero and the attacker receives the full amount. [8](#0-7)  The controller’s positive-output and final-account-risk checks can still pass because the malicious side effect is an authorization-tree injection rather than a failure to settle the displayed swap. [9](#0-8) 

### Likelihood Explanation
Exploitation requires the victim to execute a malicious route and sign the simulated authorization tree containing the extra transfer. That is nevertheless a realistic wallet-draining path when route bytes or transactions are produced by an untrusted interface, quote source, or phishing flow: the valid swap output and final position state do not reveal that an unrelated authorization child was added. The router explicitly keeps no pool/token allowlist, so the malicious contract only needs to satisfy the selected venue adapter’s ABI and deliver enough output for the route checks. [10](#0-9) 

### Recommendation
Do not let strategy payloads select arbitrary executable venue addresses. Maintain a governance-controlled venue/pool registry and reject any `assets[idx_a]` outside that registry, or replace payload-supplied venue addresses with immutable adapter-specific venue identifiers resolved from trusted storage. Until venue identities are constrained on-chain, clients must decode the route and reject any simulated authorization tree containing children other than the expected strategy transfer tree; this client check should be treated as a mitigation, not a substitute for on-chain venue validation. [11](#0-10) 

### Proof of Concept
1. Alice owns a lending account with USDC collateral and holds an unrelated wallet token.
2. The attacker deploys a contract implementing the selected venue adapter’s pool ABI. Its `swap` function invokes `wallet_token.transfer(Alice, attacker, amount)` and returns or transfers enough output token for the router’s measured-output checks.
3. The attacker encodes a `StrategyPayload` whose `assets` registry contains the malicious contract at the instruction’s pool index, with the displayed input and output assets selected by `token_in`/`token_out`. The packed program refers to those entries by index. [3](#0-2) 
4. Alice invokes `controller.swap_collateral(Alice, account_id, USDC_key, amount, ETH_key, malicious_swap_xdr)`. The controller forwards the bytes to `execute_strategy`, and the router invokes the attacker-selected pool. [12](#0-11) [6](#0-5) 
5. Simulation returns Alice’s `swap_collateral` authorization with a nested `wallet_token.transfer(Alice, attacker, amount)` child. If Alice signs that tree, the malicious transfer executes and the strategy can still complete with a solvent ETH collateral position. [13](#0-12)

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

**File:** contracts/controller/src/strategies/swap.rs (L29-38)
```rust
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

**File:** contracts/swap-aggregator/src/program.rs (L17-24)
```rust
//! instructions (5 * op_count bytes)
//!   [0]      opcode      -> Opcode
//!   [1]      mode        -> Mode
//!   [2]      idx_a       pool
//!   [3]      idx_b       token_in  | lp share token
//!   [4]      idx_c       token_out | amounts index
//! weights (3 * weight_count bytes)
//!   u24 big-endian parts-per-million, each in 1..=PPM_DENOMINATOR
```

**File:** contracts/swap-aggregator/src/program.rs (L176-183)
```rust
    /// Copies, parses, and structurally validates `ops` against the registry sizes, returning
    /// the decoded program.
    ///
    /// Panics with [`Error::InvalidRouteXdr`] on a malformed header, version, length, opcode, or
    /// index, and with a more specific error for other structural violations (empty/oversized
    /// batch, same-token swap, broken `Prev` chain, out-of-range split weight). Touches no
    /// external contract.
    pub(crate) fn decode(env: &Env, ops: &Bytes, assets_len: u32, amounts_len: u32) -> Self {
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L151-165)
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
```

**File:** contracts/swap-aggregator/src/venues/phoenix.rs (L21-25)
```rust
    ];
    ctx.authorize_pool_pull();
    let _: i128 = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &symbol_short!("swap"), args);
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
